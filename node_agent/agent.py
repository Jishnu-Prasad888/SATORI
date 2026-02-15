#!/usr/bin/env python3
"""
SATORI Node Agent
Collects system telemetry and sends to central server
"""

import os
import sys
import json
import time
import socket
import hashlib
import base64
import logging
import argparse
import platform
import subprocess
from datetime import datetime
from pathlib import Path

import requests
import psutil
from cryptography.fernet import Fernet
import netifaces

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('satori-agent')

class Config:
    """Configuration management"""
    
    CONFIG_FILE = '/etc/satori-agent/config.json'
    
    @classmethod
    def load(cls):
        """Load configuration from file"""
        if not os.path.exists(cls.CONFIG_FILE):
            return cls.create_default()
        
        with open(cls.CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    @classmethod
    def create_default(cls):
        """Create default configuration"""
        config = {
            'server_url': input('Enter server URL (e.g., http://localhost:8000): '),
            'transmission_interval': int(input('Enter transmission interval (seconds): ')),
            'api_key': input('Enter node API key: '),
            'node_name': socket.gethostname(),
            'encryption_key': 'bluematrix',  # Fixed password
            'collect_metrics': {
                'cpu': True,
                'memory': True,
                'disk': True,
                'network': True,
                'processes': True,
                'security': True,
                'kernel': True,
                'containers': True,
                'services': True
            }
        }
        
        # Save configuration
        os.makedirs(os.path.dirname(cls.CONFIG_FILE), exist_ok=True)
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    @classmethod
    def update(cls, **kwargs):
        """Update configuration"""
        config = cls.load()
        config.update(kwargs)
        
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config

class Encryptor:
    """Data encryption using fixed password"""
    
    def __init__(self, password):
        self.password = password
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)
    
    def _derive_key(self):
        """Derive Fernet key from password"""
        key = hashlib.sha256(self.password.encode()).digest()
        return base64.urlsafe_b64encode(key)
    
    def encrypt(self, data):
        """Encrypt data"""
        json_str = json.dumps(data)
        return self.fernet.encrypt(json_str.encode()).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt data"""
        decrypted = self.fernet.decrypt(encrypted_data.encode())
        return json.loads(decrypted)

class MetricCollector:
    """Collects all system metrics"""
    
    def __init__(self, config):
        self.config = config
    
    def collect_cpu(self):
        """Collect CPU metrics"""
        return {
            'overall_percent': psutil.cpu_percent(interval=1),
            'per_core': psutil.cpu_percent(interval=1, percpu=True),
            'user_time': psutil.cpu_times().user,
            'system_time': psutil.cpu_times().system,
            'idle_time': psutil.cpu_times().idle,
            'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    
    def collect_memory(self):
        """Collect memory metrics"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': mem.total,
            'available': mem.available,
            'percent_used': mem.percent,
            'used': mem.used,
            'free': mem.free,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent
        }
    
    def collect_disk(self):
        """Collect disk metrics"""
        disks = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                # Get I/O stats if available
                io_counters = psutil.disk_io_counters(perdisk=True)
                disk_io = None
                disk_name = os.path.basename(partition.device)
                
                if io_counters and disk_name in io_counters:
                    io = io_counters[disk_name]
                    disk_io = {
                        'read_count': io.read_count,
                        'write_count': io.write_count,
                        'read_bytes': io.read_bytes,
                        'write_bytes': io.write_bytes,
                        'read_time': io.read_time,
                        'write_time': io.write_time
                    }
                
                disks.append({
                    'device': partition.device,
                    'mount_point': partition.mountpoint,
                    'fs_type': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent_used': usage.percent,
                    'io_stats': disk_io
                })
            except (PermissionError, OSError):
                continue
        
        return disks
    
    def collect_network(self):
        """Collect network metrics"""
        networks = []
        net_io = psutil.net_io_counters(pernic=True)
        net_connections = psutil.net_connections()
        
        # Connection counts
        tcp_states = {}
        for conn in net_connections:
            if conn.type == socket.SOCK_STREAM:
                state = conn.status
                tcp_states[state] = tcp_states.get(state, 0) + 1
        
        for interface, addrs in psutil.net_if_addrs().items():
            if interface in net_io:
                io = net_io[interface]
                
                # Get interface speed (if available)
                speed = None
                try:
                    with open(f'/sys/class/net/{interface}/speed', 'r') as f:
                        speed = int(f.read().strip())
                except:
                    pass
                
                networks.append({
                    'interface': interface,
                    'speed': speed,
                    'status': 'up' if psutil.net_if_stats()[interface].isup else 'down',
                    'bytes_sent': io.bytes_sent,
                    'bytes_recv': io.bytes_recv,
                    'packets_sent': io.packets_sent,
                    'packets_recv': io.packets_recv,
                    'errin': io.errin,
                    'errout': io.errout,
                    'dropin': io.dropin,
                    'dropout': io.dropout,
                    'ip_addresses': [addr.address for addr in addrs if addr.family == socket.AF_INET]
                })
        
        # Get listening ports
        listening_ports = []
        for conn in net_connections:
            if conn.status == 'LISTEN' and conn.laddr:
                listening_ports.append({
                    'port': conn.laddr.port,
                    'pid': conn.pid
                })
        
        return {
            'interfaces': networks,
            'tcp_connections': tcp_states,
            'udp_count': sum(1 for conn in net_connections if conn.type == socket.SOCK_DGRAM),
            'listening_ports': listening_ports
        }
    
    def collect_processes(self):
        """Collect process metrics"""
        processes = []
        
        # Get top CPU and memory processes
        for proc in psutil.process_iter(['pid', 'ppid', 'name', 'cpu_percent', 'memory_percent', 'status', 'cmdline']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'ppid': pinfo['ppid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': pinfo['memory_percent'],
                    'status': pinfo['status'],
                    'cmdline': ' '.join(pinfo['cmdline'])[:200] if pinfo['cmdline'] else ''
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort and limit
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return {
            'total_processes': len(processes),
            'running': sum(1 for p in processes if p['status'] == 'running'),
            'sleeping': sum(1 for p in processes if p['status'] == 'sleeping'),
            'top_cpu': processes[:20],
            'top_memory': sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:20]
        }
    
    def collect_security(self):
        """Collect security metrics"""
        security_data = {
            'failed_login_attempts': 0,
            'successful_logins': 0,
            'active_users': [],
            'sudo_usage': 0,
            'new_users': [],
            'root_login_attempts': 0,
            'ssh_connections': 0
        }
        
        # Parse auth.log if available
        auth_logs = ['/var/log/auth.log', '/var/log/secure']
        for log_file in auth_logs:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-100:]  # Last 100 lines
                        
                        for line in lines:
                            if 'Failed password' in line:
                                security_data['failed_login_attempts'] += 1
                            elif 'Accepted password' in line:
                                security_data['successful_logins'] += 1
                            elif 'sudo:' in line and 'COMMAND' in line:
                                security_data['sudo_usage'] += 1
                            elif 'new user' in line:
                                security_data['new_users'].append(line.strip())
                            elif 'sshd' in line and 'Accepted' in line:
                                security_data['ssh_connections'] += 1
                except:
                    pass
        
        # Get active users
        try:
            users = subprocess.check_output(['who'], text=True).split('\n')
            security_data['active_users'] = [u.split()[0] for u in users if u]
        except:
            pass
        
        return security_data
    
    def collect_kernel(self):
        """Collect kernel metrics"""
        return {
            'kernel_version': platform.release(),
            'system_uptime': time.time() - psutil.boot_time(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'kernel_panics': self._check_kernel_panics(),
            'oom_kills': self._check_oom_kills()
        }
    
    def _check_kernel_panics(self):
        """Check for kernel panics in logs"""
        try:
            if os.path.exists('/var/log/kern.log'):
                with open('/var/log/kern.log', 'r') as f:
                    lines = f.readlines()[-1000:]
                    return sum(1 for l in lines if 'Kernel panic' in l)
        except:
            pass
        return 0
    
    def _check_oom_kills(self):
        """Check for OOM kills"""
        try:
            if os.path.exists('/var/log/syslog'):
                with open('/var/log/syslog', 'r') as f:
                    lines = f.readlines()[-1000:]
                    return sum(1 for l in lines if 'Out of memory' in l or 'oom-killer' in l)
        except:
            pass
        return 0
    
    def collect_containers(self):
        """Collect container metrics"""
        containers = []
        
        try:
            import docker
            client = docker.from_env()
            
            for container in client.containers.list():
                stats = container.stats(stream=False)
                containers.append({
                    'id': container.id[:12],
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else '',
                    'status': container.status,
                    'cpu_usage': stats['cpu_stats']['cpu_usage']['total_usage'],
                    'memory_usage': stats['memory_stats']['usage'] if 'usage' in stats['memory_stats'] else 0,
                    'network_rx': stats['networks']['eth0']['rx_bytes'] if 'eth0' in stats.get('networks', {}) else 0,
                    'network_tx': stats['networks']['eth0']['tx_bytes'] if 'eth0' in stats.get('networks', {}) else 0
                })
        except:
            pass
        
        return {
            'running_containers': len(containers),
            'containers': containers
        }
    
    def collect_services(self):
        """Collect systemd service metrics"""
        services = []
        
        try:
            import systemd.daemon
            from systemd import journal
            
            # Get all services
            output = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--all', '--no-pager'], 
                                           text=True)
            
            for line in output.split('\n')[1:-7]:  # Skip headers and footer
                parts = line.split()
                if len(parts) >= 4:
                    service = {
                        'name': parts[0],
                        'load': parts[1],
                        'active': parts[2],
                        'sub': parts[3],
                        'description': ' '.join(parts[4:])
                    }
                    
                    # Get memory usage
                    try:
                        mem = subprocess.check_output(
                            ['systemctl', 'show', parts[0], '--property=MemoryCurrent'],
                            text=True
                        ).strip()
                        if '=' in mem:
                            service['memory_usage'] = int(mem.split('=')[1])
                    except:
                        pass
                    
                    services.append(service)
        except:
            pass
        
        return {
            'total_services': len(services),
            'failed': [s for s in services if s['active'] == 'failed'],
            'running': [s for s in services if s['sub'] == 'running'],
            'services': services[:50]  # Limit to 50 services
        }
    
    def collect_all(self):
        """Collect all metrics"""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'hostname': socket.gethostname(),
            'node_name': self.config.get('node_name', socket.gethostname())
        }
        
        if self.config['collect_metrics']['cpu']:
            metrics['cpu'] = self.collect_cpu()
        
        if self.config['collect_metrics']['memory']:
            metrics['memory'] = self.collect_memory()
        
        if self.config['collect_metrics']['disk']:
            metrics['disk'] = self.collect_disk()
        
        if self.config['collect_metrics']['network']:
            metrics['network'] = self.collect_network()
        
        if self.config['collect_metrics']['processes']:
            metrics['processes'] = self.collect_processes()
        
        if self.config['collect_metrics']['security']:
            metrics['security'] = self.collect_security()
        
        if self.config['collect_metrics']['kernel']:
            metrics['kernel'] = self.collect_kernel()
        
        if self.config['collect_metrics']['containers']:
            metrics['containers'] = self.collect_containers()
        
        if self.config['collect_metrics']['services']:
            metrics['services'] = self.collect_services()
        
        return metrics

class NodeAgent:
    """Main node agent class"""
    
    def __init__(self):
        self.config = Config.load()
        self.encryptor = Encryptor(self.config['encryption_key'])
        self.collector = MetricCollector(self.config)
        self.session = requests.Session()
        self.session.headers.update({
            'X-Node-API-Key': self.config['api_key'],
            'Content-Type': 'application/json'
        })
    
    def register_node(self):
        """Register node with server"""
        try:
            response = self.session.post(
                f"{self.config['server_url']}/api/nodes/register/",
                json={
                    'hostname': socket.gethostname(),
                    'os_type': platform.system().lower(),
                    'os_version': platform.version(),
                    'kernel_version': platform.release(),
                    'cpu_cores': psutil.cpu_count(),
                    'total_memory': psutil.virtual_memory().total,
                    'ip_address': self._get_ip_address()
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                Config.update(node_id=data['node_id'])
                logger.info(f"Node registered with ID: {data['node_id']}")
                return True
            else:
                logger.error(f"Registration failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False
    
    def _get_ip_address(self):
        """Get primary IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '0.0.0.0'
    
    def send_metrics(self, metrics):
        """Send metrics to server"""
        try:
            # Encrypt metrics
            encrypted = self.encryptor.encrypt({
                'node_id': self.config.get('node_id'),
                'timestamp': metrics['timestamp'],
                'data': metrics
            })
            
            response = self.session.post(
                f"{self.config['server_url']}/api/telemetry/ingest_batch/",
                json={'data': encrypted},
                headers={'X-Encrypted': 'true'}
            )
            
            if response.status_code == 200:
                logger.debug("Metrics sent successfully")
                return True
            else:
                logger.error(f"Failed to send metrics: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    def run(self):
        """Main run loop"""
        logger.info(f"Starting SATORI Node Agent on {socket.gethostname()}")
        
        # Register if not registered
        if 'node_id' not in self.config:
            if not self.register_node():
                logger.error("Failed to register node, exiting")
                sys.exit(1)
        
        interval = self.config['transmission_interval']
        
        while True:
            try:
                # Collect metrics
                metrics = self.collector.collect_all()
                
                # Send to server
                self.send_metrics(metrics)
                
                # Wait for next collection
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description='SATORI Node Agent')
    parser.add_argument('--configure', action='store_true', help='Run configuration')
    parser.add_argument('--server-url', help='Set server URL')
    parser.add_argument('--interval', type=int, help='Set transmission interval')
    parser.add_argument('--api-key', help='Set API key')
    
    args = parser.parse_args()
    
    if args.configure:
        Config.create_default()
        return
    
    if args.server_url or args.interval or args.api_key:
        updates = {}
        if args.server_url:
            updates['server_url'] = args.server_url
        if args.interval:
            updates['transmission_interval'] = args.interval
        if args.api_key:
            updates['api_key'] = args.api_key
        
        Config.update(**updates)
        logger.info("Configuration updated")
        
        if not args.configure:  # If only updating, continue to run
            agent = NodeAgent()
            agent.run()
    else:
        agent = NodeAgent()
        agent.run()

if __name__ == '__main__':
    main()
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present Jedan Technology Solutions
"""

import multiprocessing

# Gunicorn configuration
bind = 'unix:/home/ubuntu/JedanCodeAcadamyRGBackend/base.sock'
workers = multiprocessing.cpu_count() * 2 + 1 
worker_class = 'gthread'  
threads = multiprocessing.cpu_count() * 2 
worker_connections = 1000  
timeout = 30  
keepalive = 2  
max_requests = 1000  
max_requests_jitter = 50 
preload_app = True  

# Logging configuration
accesslog = '-'  # Log to stdout
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# Security and performance optimizations
secure_scheme_headers = {
    'X-Forwarded-Proto': 'https'  
}
forwarded_allow_ips = '*' 
proxy_protocol = True  
x_forwarded_for_header = 'X-Forwarded-For'  

# Server hooks
def post_worker_init(worker):
    # Additional initialization code can be added here if needed
    pass

# Attach hooks to Gunicorn server
def on_starting(server):
    server.log.info("Starting Gunicorn server...")

def on_reload(server):
    server.log.info("Reloading Gunicorn server...")

def when_ready(server):
    server.log.info("Gunicorn server is ready to accept requests...")

def pre_fork(server, worker):
    server.log.info("Pre-forking worker {} (pid: {})...".format(worker.pid, worker.pid))

def post_fork(server, worker):
    server.log.info("Post-forking worker {} (pid: {})...".format(worker.pid, worker.pid))

def post_worker_init(worker):
    server.log.info("Initializing worker {} (pid: {})...".format(worker.pid, worker.pid))

def worker_int(worker):
    server.log.info("Worker {} (pid: {}) received INT or QUIT signal...".format(worker.pid, worker.pid))

def worker_abort(worker):
    server.log.info("Worker {} (pid: {}) aborted due to a fatal error...".format(worker.pid, worker.pid))

def pre_exec(server):
    server.log.info("Pre-execution of server process started...")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

# Include hooks in Gunicorn configuration
def post_fork(server, worker):
    post_worker_init(worker)

def worker_exit(server, worker):
    server.log.info("Worker {} (pid: {}) exited. Restarting...".format(worker.pid, worker.pid))

def worker_abort(server, worker):
    server.log.info("Worker {} (pid: {}) aborted. Restarting...".format(worker.pid, worker.pid))

def on_exit(server):
    server.log.info("Gunicorn server exiting...")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal. Exiting...")

def worker_abort(worker):
    worker.log.info("Worker aborted due to fatal error. Exiting...")

def pre_fork(server, worker):
    server.log.info("Pre-forking worker {} (pid: {})...".format(worker.pid, worker.pid))

def pre_exec(server):
    server.log.info("Pre-execution of server process started...")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers...")



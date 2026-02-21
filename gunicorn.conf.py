bind = "0.0.0.0:{}".format(__import__("os").environ.get("PORT", "5000"))
workers = 1
worker_class = "eventlet"

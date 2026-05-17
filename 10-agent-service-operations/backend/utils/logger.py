import structlog
structlog.configure(processors=[structlog.dev.ConsoleRenderer()])
logger = structlog.get_logger()
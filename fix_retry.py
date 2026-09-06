with open('src/infrastructure/retry.py', 'r') as f:
    content = f.read()

content = content.replace('before_sleep=before_sleep_log(logger, "WARNING"),', 'before_sleep=before_sleep_log(logger, 30),')

with open('src/infrastructure/retry.py', 'w') as f:
    f.write(content)

print('Fixed retry.py logging.WARNING')
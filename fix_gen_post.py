import re
with open('src/application/pipeline/steps/generate_post.py', 'r') as f:
    content = f.read()

# Use regex to find and replace
pattern = r'(                        if not template:\n                            template = get_template\("news_brief"\)\n                            template_id = "news_brief"\n\n                        # Prepare article data)'
replacement = r'                        if not template:\n                            template = get_template("news_brief")\n                            template_id = "news_brief"\n                        assert template is not None, "Template should not be None"\n\n                        # Prepare article data'

new_content = re.sub(pattern, replacement, content)

with open('src/application/pipeline/steps/generate_post.py', 'w') as f:
    f.write(new_content)

print('Fixed generate_post.py template None issue')
import re
with open('src/application/pipeline/steps/generate_post.py', 'r') as f:
    content = f.read()

# Use regex to find and replace
pattern = r'(                        if not template:\n                            template = get_template\(\
news_brief\\)\n                            template_id = \news_brief\\n\n                        # Prepare article data)'
replacement = r'                        if not template:\n                            template = get_template(\news_brief\)\n                            template_id = \news_brief\\n                        assert template is not None, \Template
should
not
be
None\\n\n                        # Prepare article data'

new_content = re.sub(pattern, replacement, content)

with open('src/application/pipeline/steps/generate_post.py', 'w') as f:
    f.write(new_content)

print('Fixed generate_post.py template None issue')

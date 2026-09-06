import re
with open('src/application/pipeline/steps/generate_post.py', 'r') as f:
    content = f.read()

# Find the exact text to replace
old_text = '                        if not template:\n                            template = get_template("news_brief")\n                            template_id = "news_brief"\n\n                        # Prepare article data'

new_text = '                        if not template:\n                            template = get_template("news_brief")\n                            template_id = "news_brief"\n                        assert template is not None, "Template should not be None"\n\n                        # Prepare article data'

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('src/application/pipeline/steps/generate_post.py', 'w') as f:
        f.write(content)
    print('Fixed generate_post.py template None issue')
else:
    print('Pattern not found, checking content...')
    idx = content.find('template_id = "news_brief"')
    if idx >= 0:
        print('Found at index:', idx)
        print(content[idx:idx+200])
    else:
        print('Not found')
# fb_auto
This package help control facebook using selenium

## Example
```python
import fb_auto
from fb_auto import action
from fb_auto import manager


account = fb_auto.new_account(cookies="fb cookie", name="account001")
posts = fb_auto.Posts()
posts.set_text(text="new posts")
posts.set_images(images=["path/img1.png", "path/img2.png"])
account.post("group_id_1", "group_id_2", posts=posts)
groups = action.get_groups(account, save_as="groups.json")
print(groups)
manager.save_and_quit(account)

account = fb_auto.open_account(name="account001")
print(account.cookies())
account.rename("new_name")
manager.save(account)
account.quit()
```
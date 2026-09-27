# Local data pack (not in Git)

Put the course data pack here before running the app:

```
data/
├── campus_customs.db     # SQLite database: catalogue, inventory, users, chat_messages
└── products/             # 102 product images (*.jpg), referenced by catalogue.image_file_path
```

Both are listed in `.gitignore` and are never committed.

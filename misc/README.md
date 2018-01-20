# CleanNotedown.py
This scipt can remove some unwanted information gengerated by Jupyter Notebook Plugin - notedown.

In the below example, `{.python .input  n=7}` is gengerated by notedown, but we don't want this to be commited. 
```
\`\`\`{.python .input  n=7}
import sys

print(sys.path)
\`\`\`
```

After processing, it will be:
```
\`\`\`
import sys

print(sys.path)
\`\`\`
```

> Note, everything after "\`\`\`" in the line will be removed.

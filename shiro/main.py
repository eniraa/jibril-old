import os

if os.name != "nt":
    import uvloop

    uvloop.install()

print("hello world")

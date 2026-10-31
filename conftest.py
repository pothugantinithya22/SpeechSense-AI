import os
# Tests must never download 1+ GB of models: force offline demo mode.
os.environ["SPEECHSENSE_OFFLINE"] = "1"
os.environ["ENABLE_HF_DOWNLOAD"] = "0"

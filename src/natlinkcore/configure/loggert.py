import logging
import sys
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)

root = logging.getLogger()
root.addHandler(handler)
root.setLevel(logging.DEBUG)
logging.debug("A")
logging.info("B")
logging.log(logging.DEBUG,"C")
print("\nD E")

from pprint import pprint
from paddlenlp import Taskflow
schema =  ['Object', 'Vegetable', 'Place']
ie_en = Taskflow('information_extraction', schema=schema, model='uie-m-large')
pprint(ie_en('In 1997, Steve was excited to become the CEO of Apple.'))

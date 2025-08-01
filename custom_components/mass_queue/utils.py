from .const import LOGGER

def get_changed_queues(old_queue, new_queue):
  LOGGER.debug(f'Getting changes between queues')
  removed = []
  added = []
  modified = []
  for k, v in old_queue.items():
    if k not in new:
      removed.append(k)
    if new[k] != v:
      modified.append(k)
  for k, v in new_queue.items():
    if k not in old_queue:
      added.append(k)
  result = {
    'added': added,
    'removed': removed,
    'modified': modified
  }
  return result

def get_changes_between_dicts(old, new):
  removed = {}
  added = {}
  modified = {}
  for k, v in old.items():
    if k not in new:
      removed[k] = v
    if new[k] != v:
      tmp = {'new_value': new[k], 'old_value': v}
      modified[k] = tmp
  for k, v in new.items():
    if k not in old:
      added[k] = v
  result = {
    'added': added,
    'removed': removed,
    'modified': modified
  }
  return result

def format_event_data_queue_item(queue_item):
  if queue_item is None:
    return None
  if queue_item.get('queue_id') is None:
    return queue_item
  item_cp = queue_item.copy()
  if 'streamdetails' in item_cp:
    item_cp.pop('streamdetails')
  if 'media_item' in item_cp:
    item_cp.pop('media_item')
  return item_cp

def format_queue_updated_event_data(event):
  event_data = event.copy()
  event_current_item = format_event_data_queue_item(event_data.get('current_item'))
  event_next_item = format_event_data_queue_item(event_data.get('next_item'))
  event_data['current_item'] = format_event_data_queue_item(event_data.get('current_item'))
  event_data['next_item'] = format_event_data_queue_item(event_data.get('next_item'))
  return event_data

def get_queue_id_from_player_data(player_data):
  try:
    ''' Force as dict if not already '''
    data = player_data.to_dict()
  except:
    pass
  current_media = data.get('current_media', None)
  if current_media is None:
    return None
  queue_id = current_media.get('queue_id')
  return queue_id
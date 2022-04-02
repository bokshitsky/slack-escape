import json

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'prepare mmctl command to insert channel'

    def configure_subparser(self, parser):
        parser.add_argument('-c', dest='channel', help='slack channel')
        parser.add_argument('-w', dest='team', help='mmt team')

    def execute_task(self, args):
        print('{"type": "version", "version": 1}')

        channel_root = self.get_channel_root(args.channel)
        channel_files_root = self.get_channel_files_root(args, channel_root)

        files = list(channel_root.glob("*.jsonl"))
        channel_new_name = self.get_channel_new_name(args.channel)
        for file in files:
            with file.open('r') as f:
                messages = (json.loads(line) for line in f)
                message = None

                while True:
                    if message is None:
                        message = next(messages, None)

                    if not message:
                        return

                    post = self.convert_message_to_post(args.channel, channel_new_name, message)
                    has_thread = 'thread_ts' in message
                    message = None

                    replies = []
                    if has_thread:
                        while True:
                            reply = next(messages, None)
                            if not reply:
                                break

                            if 'x-reply-number' not in reply:
                                message = reply
                                break

                            if reply['x-reply-number'] == 1:
                                continue

                            reply_post = self.convert_message_to_post(args.channel, channel_new_name, reply)
                            if reply_post:
                                replies.append(reply_post)

                    if replies:
                        post['replies'] = replies
                    if post:
                        print(json.dumps({
                            "type": "post",
                            "post": post
                        }, ensure_ascii=False))

    def convert_message_to_post(self, channel_old, channel_new, message):
        if message['type'] != 'message' or message.get('subtype') == 'channel_join' or 'user' not in message:
            return None

        ts = self.convert_ts(message['ts'])

        reactions = self.convert_reactions(message, ts)
        text = message.get('text', "_")

        for old_id, user in self.get_old_to_new_users_mapping().items():
            search_string = f'<@{old_id}>'
            if search_string in text:
                text = text.replace(search_string, f'@{user["new_id"]}')

        attachments = []
        for file in message.get('files', []):
            attachments.append({
                'path': f'channels/{channel_old}/files/{file["id"]}'}
            )

        post = {
            "team": "school",
            "channel": channel_new,
            "user": self.get_old_to_new_users_mapping().get(message['user'])['new_id'],
            "message": text,
            "props": {
                "attachments": [{
                    "pretext": "This is the attachment pretext.",
                    "text": "This is the attachment text."
                }]
            },
            "create_at": ts,
        }

        if reactions:
            post['reactions'] = reactions
        if attachments:
            post['attachments'] = attachments
            # post['props']: {
            #     # "attachments": [{
            #     #     "pretext": "This is the attachment pretext.",
            #     #     "text": "This is the attachment text."
            #     # }]
            # }
        return post

    def convert_reactions(self, message, ts):
        reactions = []
        for reaction in message.get('reactions', []):
            for i, user in enumerate(reaction['users'], 1):
                reactions.append({
                    "user": self.get_old_to_new_users_mapping().get(user)['new_id'],
                    "emoji_name": reaction['name'].partition('::')[0],
                    "create_at": ts + i,
                })
        return reactions

    def convert_ts(self, ts):
        return int(round(float(ts) * 1000))

    def get_channel_files_root(self, args, channel_root):
        if not channel_root.exists():
            raise RuntimeError(f"channel {args.channel} not found")
        return channel_root.joinpath("files")

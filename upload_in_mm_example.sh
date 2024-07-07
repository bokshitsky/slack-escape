cd ~/slack-escape
for d in channel1 channel2 channel3 ; do
  if [ -d ~/slack_export/channels/$d ]
  then
    python run.py mmt_prepare_channel_import_messages_file -w TEAM_NAME $d  > ~/messages/$d.jsonl
      mkdir -p ~/messages/data/channels/$d/files/
      cp ~/slack_export/channels/$d/files/* ~/messages/data/channels/$d/files/
      cd ~/messages
      zip -r $d.zip data $d.jsonl > ~/zip_log.txt
      chmod 777 $d.zip
      mv $d.zip /opt/mattermost/data/import
      echo $d
      mmctl import process $d.zip --suppress-warnings
      rm -rf ~/messages/data/channels
      cd ~/slack-escape
  else
    echo "~/slack_export/channels/$d does not not exist"
  fi
done

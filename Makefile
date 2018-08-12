download:
	rm -rf ./data
	mkdir data
	wget https://github.com/sberbank-ai/classic-ai/raw/master/examples/phonetic-baseline/data/words_accent.json.bz2 -P ./data
	wget https://raw.githubusercontent.com/sberbank-ai/classic-ai/master/data/classic_poems.json -P ./data
	wget https://bucketeer-db1966c9-c9f8-427d-ae61-659a91a9fca7.s3.amazonaws.com/public/sdsj2017_sberquad.csv -P ./data
	wget http://rusvectores.org/static/models/web_upos_cbow_300_20_2017.bin.gz -P ./data

start:
	python server.py
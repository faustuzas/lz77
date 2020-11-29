from lz77_enc import LZ77Encoder
from lz77_dec import LZ77Decoder
from loaders import ListDataLoader
from ingestors import ListDataIngestor

input_array = [
    'c', 'a', 'b', 'r', 'a', 'c',
    'a', 'd', 'a', 'b', 'r', 'a',
    'r', 'r', 'a', 'r', 'r', 'a',
    'd'
]

look_ahead_buff_size = 6
search_buff_size = 7

encoding_result_ingestor = ListDataIngestor()
encoder = LZ77Encoder(
    data_loader=ListDataLoader(input_array),
    result_ingestor=encoding_result_ingestor,
    look_ahead_buff_size=look_ahead_buff_size,
    search_buff_size=search_buff_size
)

encoder.encode()

decoding_result_ingestor = ListDataIngestor()
decoder = LZ77Decoder(
    data_loader=ListDataLoader(encoding_result_ingestor.result()),
    result_ingestor=decoding_result_ingestor,
    search_buff_size=search_buff_size
)

decoder.decode()

print(input_array == decoding_result_ingestor.result())
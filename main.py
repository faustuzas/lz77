from lz77_enc import LZ77Encoder
from lz77_dec import LZ77Decoder
from commons import FileIngestor, file_byte_data_loader, triplet_decoder, ListDataIngestor


look_ahead_buff_size = 2
search_buff_size = 5

with open('encoded.lz77', 'wb') as f:
    encoding_result_ingestor = FileIngestor(f)
    list_ingestor = ListDataIngestor()
    encoder = LZ77Encoder(
        data_loader=file_byte_data_loader('a1.txt'),
        # data_loader=file_byte_data_loader('input_foto.jpeg'),
        # result_ingestor=encoding_result_ingestor,
        result_ingestor=list_ingestor,
        look_ahead_buff_size=look_ahead_buff_size,
        search_buff_size=search_buff_size
    )

    encoder.encode()

print(list_ingestor.result())

# with open('output_foto.jpeg', 'wb') as f:
# with open('a1-output.txt', 'wb') as f:
#     decoding_result_ingestor = FileIngestor(f)
#     decoder = LZ77Decoder(
#         data_loader=triplet_decoder(file_byte_data_loader('encoded.lz77')),
#         result_ingestor=decoding_result_ingestor,
#         search_buff_size=search_buff_size
#     )
#
#     decoder.decode()

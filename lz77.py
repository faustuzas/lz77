#! /usr/bin/python3
import argparse

from lz77_enc import LZ77Encoder
from lz77_dec import LZ77Decoder
from commons import EncodingFileTripletIngestor, file_byte_data_loader, triplet_decoder


look_ahead_buff_size = 200
search_buff_size = 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LZ77 based encoder')
    parser.add_argument('--type', choices=['enc', 'dec'], default='enc')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    type_ = args.type
    input_file = args.input
    output_file = args.output
    if type_ is None or input_file is None or output_file is None:
        parser.print_help()
        exit(-2)

    with EncodingFileTripletIngestor(output_file) as ingestor:
        data_loader = file_byte_data_loader(input_file)

        if type_ == 'enc':
            encoder = LZ77Encoder(
                data_loader=data_loader,
                result_ingestor=ingestor,
                look_ahead_buff_size=look_ahead_buff_size,
                search_buff_size=search_buff_size
            )

            encoder.encode()
        else:
            decoder = LZ77Decoder(
                data_loader=triplet_decoder(data_loader),
                result_ingestor=ingestor,
                search_buff_size=search_buff_size
            )

            decoder.decode()

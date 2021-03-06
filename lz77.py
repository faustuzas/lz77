import argparse

from lz77_enc import LZ77Encoder
from lz77_dec import LZ77Decoder
import commons


def main():
    parser = argparse.ArgumentParser(description='LZ77 based encoder')
    parser.add_argument('--type', choices=['enc', 'dec'], default='enc')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--offset_size', required=False)
    parser.add_argument('--match_len_size', required=False)
    args = parser.parse_args()

    type_ = args.type
    input_file = args.input
    output_file = args.output
    if type_ is None or input_file is None or output_file is None:
        parser.print_help()
        exit(-2)

    if type_ == 'enc':
        offset_size_in_bits = args.offset_size or None
        match_len_size_in_bits = args.match_len_size or None
        if offset_size_in_bits is None or match_len_size_in_bits is None:
            parser.print_help()
            exit(-2)

        offset_size_in_bits = int(offset_size_in_bits)
        match_len_size_in_bits = int(match_len_size_in_bits)

        with commons.FileRawDataLoader(input_file) as loader:
            with commons.EncodingFileTripletIngestor(output_file,
                                                     offset_size_in_bits,
                                                     match_len_size_in_bits) as ingestor:
                encoder = LZ77Encoder(
                    data_loader=loader,
                    result_ingestor=ingestor,
                    search_buff_size=commons.search_buff_size_for_bits(offset_size_in_bits),
                    look_ahead_buff_size=commons.look_ahead_size_for_bits(match_len_size_in_bits)
                )

                encoder.encode()
        return

    if type_ == 'dec':
        with commons.DecodingFileTripletLoader(input_file) as loader:
            with commons.FileRawDataIngestor(output_file) as ingestor:
                (offset_size_in_bits, _) = loader.encoding_meta_data

                decoder = LZ77Decoder(
                    data_loader=loader,
                    result_ingestor=ingestor,
                    search_buff_size=commons.search_buff_size_for_bits(offset_size_in_bits)
                )

                decoder.decode()

                return

    print(f'Error: type ${type_} is not recognized')


if __name__ == '__main__':
    main()

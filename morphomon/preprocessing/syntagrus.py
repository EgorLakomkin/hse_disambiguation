import codecs
import lxml.html
import settings

def get_token_str_rep(el):
    gram = el.attrib["feat"]
    lemma = el.attrib["lemma"]
    word_form = el.text
    lemma_str = u"{0}={1}".format( lemma, ','.join(gram.split(' ')) )
    result_str = u"{0}\t{1}\r\n".format(word_form,lemma_str)
    return result_str

def process_syntagrus_file( file, outfile ):
    out_f =  codecs.open( outfile, 'w', 'utf-8' )
    f = codecs.open( file, 'r', 'utf-8' )
    try:
        content = f.read()
        document = lxml.html.document_fromstring( content )
        sentences = document.xpath("//s")
        for sentence in sentences:
            for el in sentence.findall(".//w"):
                out_f.write(get_token_str_rep( el ))
            out_f.write('\r\n')

    except Exception as e:
        raise Exception("Dom parsing exception %s" % (e))

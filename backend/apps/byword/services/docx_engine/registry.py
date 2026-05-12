from apps.byword.services.docx_engine.renderers import (
    render_text,
    render_image,
    render_title_right,
    render_table_2_columns,
    render_reference_right,
    render_dictionary_table,
    render_scramble_table,
    render_wordsearch_image,
    render_scramble_sentences,
)

DOCX_RENDERERS = {
    "text": render_text,
    "image": render_image,
    "title_right": render_title_right,
    "table_2_columns": render_table_2_columns,
    "reference_right": render_reference_right,
    "dictionary_table": render_dictionary_table,
    "scramble_table": render_scramble_table,
    "wordsearch_image": render_wordsearch_image,
    "scramble_sentences": render_scramble_sentences,
}

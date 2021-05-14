import re
import json

from google.cloud import documentai_v1 as documentai
from google.cloud import storage

# TODO(developer): Uncomment these variables before running the sample.
# project_id= ''
# location = 'us' # Format is 'us' or 'eu'
# processor_id = '' # Create processor in Cloud Console
# gcs_input_uri = ""
# gcs_output_uri = ""
# gcs_output_uri_prefix = ""


def batch_process_documents(
    project_id,
    location,
    processor_id,
    gcs_input_uri,
    gcs_output_uri,
    gcs_output_uri_prefix,
    timeout: int = 300,
):

    # You must set the api_endpoint if you use a location other than 'us', e.g.:
    opts = {}
    if location == "eu":
        opts = {"api_endpoint": "eu-documentai.googleapis.com"}

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}/"

    gcs_documents = documentai.GcsDocuments(
        documents=[{"gcs_uri": gcs_input_uri, "mime_type": "application/pdf"}]
    )

    # 'mime_type' can be 'application/pdf', 'image/tiff',
    # and 'image/gif', or 'application/json'
    input_config = documentai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)

    # Where to write results
    output_config = documentai.DocumentOutputConfig(
        gcs_output_config={"gcs_uri": destination_uri}
    )

    # Location can be 'us' or 'eu'
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
    request = documentai.types.document_processor_service.BatchProcessRequest(
        name=name,
        input_documents=input_config,
        document_output_config=output_config,
    )

    # operation = client.batch_process_documents(request)

    # # Wait for the operation to finish
    # operation.result(timeout=timeout)

    # Results are written to GCS. Use a regex to find
    # output files
    match = re.match(r"gs://([^/]+)/(.+)", destination_uri)
    output_bucket = match.group(1)
    prefix = match.group(2)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(output_bucket)
    blob_list = list(bucket.list_blobs(prefix=prefix))
    print("Output files:")
    outputPages = []
    
    for i, blob in enumerate(blob_list):
        # If JSON file, download the contents of this blob as a bytes object.
        if ".json" in blob.name:
            blob_as_bytes = blob.download_as_bytes()

            document = documentai.types.Document.from_json(blob_as_bytes)
            print(f"Fetched file {i + 1}: {blob.name}")

            # For a full list of Document object attributes, please reference this page:
            # https://cloud.google.com/document-ai/docs/reference/rpc/google.cloud.documentai.v1beta3#document

            # Read the text recognition output from the processor
            for page in document.pages:
                outputPage = {
                    "title": "",
                    "quote": "",
                    "author": "",
                    "commentary": ""
                }
                for form_field in page.form_fields:
                    field_name = get_text(form_field.field_name, document)
                    field_value = get_text(form_field.field_value, document)
                    print("Extracted key value pair:")
                    print(f"\t{field_name}, {field_value}")
                # for paragraph in document.paragraphs:
                #     paragraph_text = get_text(paragraph.layout, document)
                #     # print(f"Paragraph text:\n{paragraph_text}")
                if len(page.paragraphs) > 3:
                    outputPage['title'] = get_text(page.paragraphs[0].layout, document)
                    outputPage['quote'] = get_text(page.paragraphs[1].layout, document)
                    outputPage['author'] = get_text(page.paragraphs[2].layout, document)
                    outputCommentary = ""
                    for commentaryI in range(3,len(page.paragraphs)):
                        outputCommentary = outputCommentary + get_text(page.paragraphs[commentaryI].layout,document)
                    outputPage['commentary'] = outputCommentary

                    # outputPage['commentary'] = get_text(page.paragraphs[3:len(page.paragraphs)-1])
                # for paragraph in page.paragraphs:
                #     paragraph_text = get_text(paragraph.layout, document)
                #     print(f"Paragraph text:\n{paragraph_text}")
                outputPages.append(outputPage)

        else:
            print(f"Skipping non-supported file type {blob.name}")
    with open("output.json", "w") as outfile: 
        json.dump(outputPages, outfile)


# Extract shards from the text field
def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    num = 0
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
        # print(f"Segment {num} text:\n{document.text[start_index:end_index]}")
        num = num + 1
    return response


batch_process_documents(
    project_id,
    location,
    processor_id,
    gcs_input_uri,
    gcs_output_uri,
    gcs_output_uri_prefix
)

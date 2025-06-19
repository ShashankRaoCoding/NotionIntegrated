from django.http import HttpResponse
from notion_client import Client
from . import llm 
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

notion = Client(auth="NOTION_KEY_HERE")  

def index(request): 
    pidwnames = getAllPageIDsWNames() 
    return render(request, "pageSelect.html", {"pidwnames": pidwnames})

@csrf_exempt
def SummarisePage(request):
    if request.method == "POST":
        pid = request.POST.get("page_id")  
        if pid:
            data = getPageData(pid) 
            response = llm.lookup_with_claude(data + "summarise this and style it like a LinkedIn post") 
            return HttpResponse(response)
        else:
            return HttpResponse("No page selected", status=400)
    else:
        return HttpResponse("Invalid method", status=405)

def getAllPageIDsWNames(): 
    i = {} 
    pidswfilenames = get_page_ids_and_filenames() 
    for pid, filename in pidswfilenames: 
        i[pid] = filename
    return i 

def get_page_ids_and_filenames():
    pages = []

    has_more = True
    next_cursor = None

    while has_more:
        response = notion.search(
            query="",
            filter={"value": "page", "property": "object"},
            start_cursor=next_cursor
        )

        for result in response["results"]:
            page_id = result["id"]
            title = "Untitled"

            # Try database title
            properties = result.get("properties", {})
            for prop in properties.values():
                if prop.get("type") == "title":
                    title_parts = prop.get("title", [])
                    title = "".join([part["plain_text"] for part in title_parts])
                    break

            # Fallback: try to get first block text as title
            if title == "Untitled":
                try:
                    children = notion.blocks.children.list(page_id)
                    for block in children["results"]:
                        if "paragraph" in block:
                            texts = block["paragraph"].get("text", [])
                            title = "".join([t["plain_text"] for t in texts])
                            if title:
                                break
                except:
                    pass  # some pages may not allow access or be empty

            pages.append((page_id, title))

        has_more = response.get("has_more", False)
        next_cursor = response.get("next_cursor")

    return pages

def create_summary_page(parent_page_id, summary_text, title="Summary"):
    notion.pages.create(
        parent={"page_id": parent_page_id},
        properties={
            "title": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": summary_text
                            }
                        }
                    ]
                }
            }
        ]
    )


def getPageData(PAGE_ID): 

    page_content = "" 

    content = get_all_blocks(PAGE_ID)
    for block in content:
        block_type = block.get("type")
        text_info = block.get(block_type, {}).get("rich_text", [])
        text = "".join([t.get("plain_text", "") for t in text_info])
        page_content += text 
    return page_content 

def get_all_blocks(block_id):
    blocks = []
    cursor = None

    while True:
        response = notion.blocks.children.list(block_id, start_cursor=cursor)
        blocks.extend(response['results'])
        cursor = response.get('next_cursor')
        if not cursor:
            break

    # Recursively get children of children
    for block in blocks:
        if block.get("has_children"):
            block["children"] = get_all_blocks(block["id"])
    return blocks

def summarise(pid):
    data = getPageData(pid)
    prompt = data + "Here is the content of my week. Please produce:\n\n"
                "1. A brief summary of what I did this week.\n"
                "2. A list of concise bullet points suitable for my CV.\n\n"
                "Only output these two parts, clearly labelled."
                "\n\nContent:\n"
    # response_stream = llm.lookup_with_llama(prompt)
    
    # # Wrap the generator with StreamingHttpResponse for streaming
    # return StreamingHttpResponse(response_stream, content_type='text/plain')

    response = llm.lookup_with_claude(prompt) 
    return HttpResponse(response) 

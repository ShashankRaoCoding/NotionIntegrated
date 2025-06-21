from django.http import HttpResponse
from notion_client import Client
from . import llm 
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

notion = Client(auth=open("notion_key.txt", "r").readlines()[0].strip())  

def index(request): 
    pidwnames = getAllPageIDsWNames() 
    return render(request, "pageSelect.html", {"pidwnames": pidwnames})

@csrf_exempt
def SummarisePage(request):
    if request.method == "POST":
        pid = request.POST.get("page_id")  
        if pid:
            data = getPageData(pid) 
            response = llm.lookup_with_claude(data + "You are helping me organise my weekly work journal into a structured Notion page.\nBased on the content below, extract two sections:\n1. Actionable Points: clear, specific tasks or decisions that can be followed up on. Use bullet points.\n2. CV Points: concise, resume-style bullet points highlighting skills demonstrated, impact, or achievements. Use action verbs.\nKeep the language clean and professional. Only output these two sections, each with a bold heading.") 
            create_summary_page(pid, response, "Summary") 
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

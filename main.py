
from flask import Flask,Response,render_template_string, request,jsonify,make_response,redirect ,session,render_template,url_for,send_from_directory
import os
from flask_cors import CORS
import aiohttp
import asyncio
from datetime import datetime,timedelta,timezone
#from controllers import *
import json
#from daraja import *
from werkzeug.utils import secure_filename
from oauthlib.oauth2 import WebApplicationClient
import requests
import base64
from pytrends.request import TrendReq
app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app.secret_key = 'ussd'

apiServer = "https://api.webdocedit.com"
#apiServer = "http://localhost"
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            

@app.route('/api/trending', methods=['GET'])
def get_trending_keywords():
    pytrends = TrendReq(hl='en-US', tz=360)

    trending_searches = pytrends.trending_searches(pn='india')  
    trending_keywords = trending_searches[0].tolist()
    return jsonify(trending_keywords)
    
@app.route('/robots.txt')
def robots_txt():
    content = "User-agent: *\nAllow:*\nDisallow:"
    return Response(content, mimetype='text/plain')
    
@app.route('/ads.txt')
def ads_txt():
    content = "google.com, pub-8402082494280043, DIRECT, f08c47fec0942fa0"
    return Response(content, mimetype='text/plain')
    
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []

    # Get all the static routes in the Flask app
    for rule in app.url_map.iter_rules():
        if 'GET' in rule.methods and not rule.arguments:
            url = url_for(rule.endpoint, _external=True)
            pages.append([url, datetime.now()])

    # Generate the XML for the sitemap
    sitemap_xml = render_sitemap(pages)

    return Response(sitemap_xml, mimetype='application/xml')


def render_sitemap(pages):
    # Create the XML structure
    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for page in pages:
        sitemap_xml.append('<url>')
        sitemap_xml.append(f'<loc>{page[0]}</loc>')
        sitemap_xml.append(f'<lastmod>{page[1].strftime("%Y-%m-%dT%H:%M:%S+00:00")}</lastmod>')
        sitemap_xml.append('</url>')

    sitemap_xml.append('</urlset>')

    return '\n'.join(sitemap_xml)


    
GEOLOCATION_API_URL = "https://ipapi.co/{}/json/"

async def fetch_country(ip_address):
    async with aiohttp.ClientSession() as session:
        async with session.get(GEOLOCATION_API_URL.format(ip_address)) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("country_name", "Unknown")
            else:
                return "Unknown"
                
@app.route('/ip')
def get_ip():
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        ip_address = forwarded_for.split(',')[0]
    else:
        ip_address = request.remote_addr

@app.before_request
async def before_request_func():
    if session.get("manifest") == None:
        session["manifest"] = {
            "title": "WebDocEdit",
            "tools":[
                {"merge_pdf":{"title":"Merge PDF","svg":"","description":"Combine PDFs in the order you want with the easiest PDF merger available.","new":True,"category":"ORGANIZE PDF" }},
                {"split_pdf":{"title":"Split PDF","svg":"","description":"Separate one page or a whole set for easy conversion into independent PDF files.","new":True,"category":"ORGANIZE PDF"}},
                {"remove_pages":{"title":"Remove Pages","svg":"","description":"Select and remove the PDF pages you don’t need. Get a new file without your deleted pages.","new":True,"category":"ORGANIZE PDF"}},
                {"organize_pdf":{"title":"Organize PDF","svg":"","description":"Sort, add and delete PDF pages.Drag and drop the page thumbnails and sort them in our PDF organizer.","new":True,"category":"ORGANIZE PDF"}},
                {"compress_pdf":{"title":"Compress PDF","svg":"","description":"Reduce file size while optimizing for maximal PDF quality.","new":True,"category":"OPTIMIZE PDF"}},
                {"repair_pdf":{"title":"Repair PDF","svg":"","description":"Upload a corrupt PDF and we will try to fix it.","new":True,"category":"OPTIMIZE PDF"}},
                #{"ocr_pdf":{"title":"OCR PDF","svg":"","description":"Convert non-selectable PDF files into selectable and searchable PDF with high accuracy.","new":True,"category":"OPTIMIZE PDF"}},
                {"jpg_to_pdf":{"title":"JPG to PDF","svg":"","description":"Convert JPG images to PDF in seconds. Easily adjust orientation and margins.","new":True,"category":"CONVERT TO PDF"}},
                {"ppt_to_pdf":{"title":"PPT to PDF","svg":"","description":"Make PPT and PPTX slideshows easy to view by converting them to PDF.","new":True,"category":"CONVERT TO PDF"}},
                {"excel_to_pdf":{"title":"EXCEL to PDF","svg":"","description":"Convert Excel spreadsheets to PDF.","new":True,"category":"CONVERT TO PDF"}},
                {"html_to_pdf":{"title":"HTML to PDF","svg":"","description":"Convert HTML Web pages to PDF.","new":True,"category":"CONVERT TO PDF"}},
                {"pdf_to_jpg":{"title":"PDF to JPG","svg":"","description":"Convert each PDF page into a JPG or extract all images contained in a PDF.","new":True,"category":"CONVERT FROM PDF"}},
                {"pdf_to_word":{"title":"PDF to WORD","svg":"","description":"Convert your PDF to WORD documents with incredible accuracy.","new":True,"category":"CONVERT FROM PDF"}},
                {"pdf_to_ppt":{"title":"PDF to PPT","svg":"","description":"Convert your PDFs to POWERPOINT.","new":True,"category":"CONVERT FROM PDF"}},
                {"pdf_to_excel":{"title":"PDF to Excel","svg":"","description":"Convert your PDFs to Excel SpreadSheets.","new":True,"category":"CONVERT FROM PDF"}},
                {"rotate_pdf":{"title":"Rotate PDF","svg":"","description":"Rotate your PDFs the way you need them. You can even rotate multiple PDFs at once!","new":True,"category":"EDIT PDF"}},
                {"add_page_number":{"title":"Add PDF page numbers","svg":"","description":"Add page numbers into PDFs with ease. Choose your positions, dimensions, typography.","new":True,"category":"EDIT PDF"}},
                {"add_watermark":{"title":"Watermark PDF","svg":"","description":"Stamp an image or text over your PDF in seconds. Choose the typography, transparency and position.","new":True,"category":"EDIT PDF"}},
                #{"remove_watermark":{"title":"Remove Watermark from a PDF","svg":"","description":"Remove image over your PDF in seconds. Choose the typography, transparency and position.","new":True,"category":"EDIT PDF"}},
                
                {"compare_pdf":{"title":"Compare PDF","svg":"","description":"Easily display the differences between two similar files.","new":True,"category":"PDF SECURITY"}},
                {"redact_pdf":{"title":"Redact PDF","svg":"","description":"Remove sensitive content from PDFs","new":True,"category":"PDF SECURITY"}},
                {"sign_pdf":{"title":"Sign PDF","svg":"","description":"Your tool to eSign documents. Sign a document yourself or send a signature request to others.","new":True,"category":"PDF SECURITY"}},
                {"protect_pdf":{"title":"Encrypt PDF","svg":"","description":"Encrypt your PDF with a password to keep sensitive data confidential.","new":True,"category":"PDF SECURITY"}},
                {"unlock_pdf":{"title":"Decrypt PDF","svg":"","description":"Remove PDF password security, giving you the freedom to use your PDFs as you want.","new":True,"category":"PDF SECURITY"}},
                {"edit_pdf":{"title":"Edit PDF","svg":"","description":"Edit PDF by adding text, shapes, comments and highlights. Your secure and simple tool to edit PDF.","new":True,"category":"EDIT PDF"}}
            ],
            "categories":["ORGANIZE PDF","OPTIMIZE PDF","CONVERT TO PDF","CONVERT FROM PDF","EDIT PDF","PDF SECURITY"]
        }
        
    if session.get("user") == None:
        session["manifest"]["user"] = {}
        session["manifest"]["country"] = await fetch_country(get_ip)
    else:
        session["manifest"]["user"] = session.get("user")
        session["manifest"]["country"] = await fetch_country(get_ip)
        
@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    if not url:
        return Response("No URL provided", status=400)
    
    try:
        resp = requests.get(url, stream=True)
        if resp.status_code == 200:
            headers = {
                'Content-Type': resp.headers['Content-Type'],
                'Access-Control-Allow-Origin': '*'
            }
            return Response(resp.content, headers=headers)
        else:
            return Response("Error fetching the image", status=500)
    except Exception as e:
        return Response(f"Error fetching the image: {e}", status=500)

@app.route('/static/uploads/<path:filename>')
def serve_static(filename):
    try:
        response = make_response(send_from_directory('static/uploads', filename))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=' + filename
        return response
    except FileNotFoundError:
        abort(404)
        
@app.route("/libpdf/<string:id>/<path:file_dir>")
def webview_utils(id,file_dir):
    print(file_dir)
    file_dir = file_dir.replace(".map","")
    return send_from_directory("static/",path=file_dir)
    
@app.route("/trueedit_libpdf/<string:id>/core/pdf/<path:file_dir>")
def corePDF(id,file_dir):
    return send_from_directory("static/core/pdf/",path=file_dir)
    
@app.route("/libpdf/<string:id>/ui/index.html")
@app.route("/trueedit_libpdf/<string:id>/ui/index.html")
def webview(id):
    return render_template("webview/index.html",manifest=session['manifest'])
@app.route("/libpdf/<string:id>/ui/<path:file_dir>")
@app.route("/trueedit_libpdf/<string:id>/ui/<path:file_dir>")
def webview_files(id,file_dir):
    print(id)
    #return render_template("webview/index.html",manifest=session['manifest'])
    return send_from_directory("static/",path=file_dir)

@app.route("/stripe/execute",methods=["POST"])
def stripe_pay():
    print(request.form)
    return jsonify({})
    
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT","")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_SECRET","")
PAYPAL_TOKEN_URL = 'https://api.paypal.com/v1/oauth2/token'
PAYPAL_SUBSCRIPTION_URL = 'https://api.paypal.com/v1/billing/subscriptions'

def get_paypal_access_token():
    auth = base64.b64encode(f'{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    response = requests.post(PAYPAL_TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print((f"Failed to get access token: {response.text}"))
        return None
        
@app.route("/paypal/cancel",methods=["POST","GET"])
def paypal_cancel():
    print("response=>",response.json if response.json else {})
    return "Cancelled Response"
    
@app.route("/paypal/success",methods=["POST","GET"])
def paypal_success():
    print("response=>",response.json if response.json else {})
    return "Success Response"

@app.route("/paypal/create",methods=["POST"])
def paypal_pay():
    print(request.form)
    try:
        # Get access token
        access_token = get_paypal_access_token()

        # Define subscription details
        subscription_data = {
            "plan_id": "P-XXXXXXXXXX",  # Replace with your plan ID
            "application_context": {
                "brand_name": "WEBDOCEDIT",
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING", # Set according to your needs
                "user_action": "SUBSCRIBE_NOW",
                "return_url": "https://www.webdocedit.com/paypal/return",  # Replace with your return URL
                "cancel_url": "https://www.webdocedit.com/paypal/cancel"    # Replace with your cancel URL
            }
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(PAYPAL_SUBSCRIPTION_URL, headers=headers, json=subscription_data)
        if response.status_code == 201:
            subscription = response.json()
            approval_url = next(link['href'] for link in subscription['links'] if link['rel'] == 'approve')
            print("approval_url",approval_url)
            return jsonify({'approval_url': approval_url})
        else:
            return jsonify({'error': 'Failed to create subscription', 'details': response.json()}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500       
@app.route('/help/terms')
@app.route('/terms-of-use') 
@app.route('/terms')
def terms():
    return render_template('terms.html',manifest=session["manifest"])

@app.route('/help/privacy')
@app.route('/privacy-policy')
@app.route('/privacy')
def privacy():
    return render_template('privacy-policy.html',manifest=session["manifest"])
    
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID',"")#session["manifest"]["google-client"]
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET',"")#session["manifest"]["google-secret"]
client = WebApplicationClient(GOOGLE_CLIENT_ID)
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
    
@app.route("/auth/auth")
def authPage():
    auth_type = request.args.get("authclient")
    request_uri = "https://www.webdocedit.com/login"
    if auth_type == "google":
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri="https://www.webdocedit.com/login/callback",
            scope=["openid","email", "profile"],
        )
        
        return redirect(request_uri)
        
    else:
        return redirect(request_uri)
    
@app.route("/problem/<string:tool>/<string:key>/")
def error_merge2(tool,key):
    error_message = "An error occured during "+tool+"<a href='/'>Home</a>"
    return render_template_string(error_message), 400
    
@app.route("/problem/<string:tool>/<string:key>/<int:id>")
@app.route("/problem/<string:tool>/<string:key>/<int:id>/ServerError")
def error_merge(tool,key,id):
    error_message = "An error occured during "+tool+"<a href='/'>Home</a>"
    return render_template_string(error_message), 400


@app.route("/download/<int:id>/<string:key>")
def success_download(id,key):
    print("id",id)
    global apiServer
    return render_template("download.html",url_key=key,url_id=id,manifest=session["manifest"],apiServer=apiServer)

@app.route("/")
def index():
    session["manifest"]["tools"] = session["manifest"]["tools"][::-1]
    session["manifest"]["categories"] = session["manifest"]["categories"][::-1]
    return render_template("index.html",manifest=session["manifest"])

@app.route("/user",methods=["GET","POST"])
def user():
    print("user=>",session["manifest"].get("user"))
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("user.html",manifest=session["manifest"])

@app.route("/user/premium")
def user_premium():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("register"))
    return render_template("premium.html",manifest=session["manifest"]) 

@app.route("/user/security")
def user_security():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("security.html",manifest=session["manifest"]) 

@app.route("/user/team")
def user_team():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("team.html",manifest=session["manifest"]) 

@app.route("/user/history")
def user_history():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("history.html",manifest=session["manifest"]) 

@app.route("/user/signatures")
def user_signatures():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("signatures.html",manifest=session["manifest"]) 
@app.route("/user/signatures/requests")
def user_signatures_request():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("signatures_request.html",manifest=session["manifest"]) 

@app.route("/user/signatures/pending")
def user_signatures_pending():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("signatures_pending.html",manifest=session["manifest"]) 

@app.route("/user/signatures/signed")
def user_signatures_signed():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("signatures_signed.html",manifest=session["manifest"]) 

@app.route("/user/signatures/templates")
def user_signatures_templates():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("signatures_templates.html",manifest=session["manifest"]) 

@app.route("/user/signatures/settings")
def user_signature_settings():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("signatures_settings.html",manifest=session["manifest"]) 

@app.route("/user/contacts")
def user_contacts():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("contacts.html",manifest=session["manifest"]) 

@app.route("/user/plan")
def user_plan():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("plan.html",manifest=session["manifest"]) 

@app.route("/user/business")
def user_business():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None or session["manifest"]["user"].get("authentication") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("user_business.html",manifest=session["manifest"]) 

@app.route("/user/invoices")
def user_invoices():
    if session["manifest"].get("user") == None or session["manifest"]["user"].get("authentication") == None:
        return redirect(url_for("logout"))
    return render_template("user_invoices.html",manifest=session["manifest"]) 
    
@app.route("/user/team/invite")
def user_invite():
    return render_template("user_teams.html",manifest=session["manifest"]) 

@app.route("/pricing")
def pricing():
    return render_template("pricing.html",manifest=session["manifest"])

@app.route("/business")
def business():
    return render_template("business.html",manifest=session["manifest"])

@app.route("/education")
def education():
    return render_template("education.html",manifest=session["manifest"])

@app.route("/features")
def features():
    return render_template("features.html",manifest=session["manifest"])

@app.route("/desktop")
def desktop():
    return render_template("desktop.html",manifest=session["manifest"])

@app.route("/mobile")
def mobile():
    return render_template("mobile.html",manifest=session["manifest"])

@app.route("/contact",methods=['GET','POST'])
def contact():
    return render_template("contact.html",manifest=session["manifest"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
    
@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
   

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    print("token response",token_response.text)
    client.parse_request_body_response(token_response.text)

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["name"]
        headers = {
                #'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        data = {'email':users_email,'password':"google","name": users_name}
        response = requests.post(apiServer+"/api/auth", headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            #return response.json().get('access_token')
            print(response.content)
            return redirect("login?message="+str(response.content))
        result = response.json()
        session['google_id'] = unique_id
        session["manifest"]["user"]['name'] = users_name
        session["manifest"]["user"]['email'] = users_email
        session["manifest"]["user"]['picture'] = picture
        session["manifest"]["user"]["authentication"] = "google"
        session["manifest"]["user"]["token"] = result.get('token')
        session["user"] =session["manifest"]["user"]
        print("user=>",session["manifest"]["user"])
    else:
        return "User email not available or not verified by Google.", 400

    return redirect(url_for("user"))

@app.route("/login",methods=["GET","POST"])
def login():
    if session.get("manifest").get("user").get("authentication") != None:
        #return redirect(url_for('logout'))
        session.get("manifest")["user"] = {}
    if request.method == "POST":
        print(request.form)
        email = request.form["LoginForm[email]"]
        password = request.form["LoginForm[password]"]
        if email and password:
            headers = {
                #'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            data = {'email':email,'password':password}
            response = requests.post(apiServer+"/api/auth", headers=headers, data=json.dumps(data))
            if response.status_code != 200:
                #return response.json().get('access_token')
                print(response.content)
                return redirect("login?message="+response.json().get('message'))
            result = response.json()
            
            session["user"] = {"name":result['payload']['name'],"email":result['payload']['email'],"plan":0,"premium":result['payload']['premium'],"country":"KE","token":result.get('token'),"authentication":"login"}
            session["manifest"]["user"] = session["user"]
            return redirect("user")
    return render_template("login.html",manifest=session["manifest"])

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["SignupForm[name]"]
        email = request.form["SignupForm[email]"]
        password = request.form["SignupForm[password]"]
        if name and email:
            headers = {
                #'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            data = {'name': name,'email':email,'password':password}
            response = requests.post(apiServer+"/api/users/register", headers=headers, data=json.dumps(data))
            #response = response.content
            print("response",str(response))
            if response.status_code == 200:
                #return response.json().get('access_token')
                return redirect("login?message="+response.json().get('message'))
            else:
                return redirect("register?message="+response.json().get('message'))
        else:    
            return redirect(url_for("index"))
    return render_template("register.html",manifest=session["manifest"])

@app.route("/templates/<string:name>")
def load_template(name):
    url_key = request.args.get("tool")
    url_id = request.args.get("taskId")
    global apiServer
    return render_template("template/"+name+".html",apiServer=apiServer,manifest=session["manifest"],**locals())

@app.route("/templates/<string:name>/<string:name_n>")
def load_template_n(name,name_n):
    return render_template("template/"+name+"/"+name_n+".html",manifest=session["manifest"])
@app.route("/<string:title>")
def function(title):
    if session.get("manifest") == None or session["manifest"].get("tools") == None:
        return redirect(url_for('logout'))
    found = None
    if title:
        for tool in session["manifest"]["tools"]:
            for key in tool.keys():
                if key == title:
                    print("tool",tool)
                    found = tool[key]
                    found["tool"] = key
    if found != None:
        return render_template("tools/"+found["tool"]+".html",manifest=session["manifest"],tool=found)
    return render_template("tool.html",manifest=session["manifest"],tool=found)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message='Page Not Found'), 404
    
@app.errorhandler(400)
def error_found(e):
    return render_template('error.html', error_code=400, error_message='Bad Error '), 400

# Error handler for 500 errors
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message='Internal Server Error'), 500

    


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))#host="0.0.0.0",
    app.run( port=port,debug=True )

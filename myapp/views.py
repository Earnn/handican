from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate,update_session_auth_hash
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect,HttpResponse,Http404
from myapp.models import *
from django.views.generic.edit import UpdateView
from django.db.models import Q
import difflib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# change password
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import Http404
from datetime import date
from .forms import *

# Create your views here.
def home(request):

    if request.user.is_authenticated():

        if request.user.groups.filter(name='company').exists():
            return redirect('employer_search')
        else:
            return redirect('search')
    else :

        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                email= form.cleaned_data.get('email')
                name = form.cleaned_data.get('name')
                phone= form.cleaned_data.get('phone')
                subject = form.cleaned_data.get('subject')
                message= form.cleaned_data.get('message')
                status = True

                Contact.objects.create(email=email,name=name,phone=phone,subject=subject,message=message)

            return render(request, 'home.html',{'username': request.user.username,'form':form,'status':status})


        else :
            form = ContactForm()    
    return render(request, 'home.html',{'username': request.user.username,'form':form})

    


def disable_detail(request,dis_id,job_id):
    dis = DisabilityInfo.objects.get(id=dis_id)
    status = "ยังไม่ส่งคำเชิญ"
    job = Job.objects.get(id=job_id)
    try :
        status = InviteProcess.objects.get(disability=dis,job__id=job_id)
        status = status.status

    except :
        pass

    return render(request, 'disable_detail.html', {'dis':dis,'status':status,'job':job})

def invite_job_to_disability(request,dis_id,job_id):
    tarket = DisabilityInfo.objects.get(id=dis_id)
    
  
    job = Job.objects.get(id=job_id)

    Notifications.objects.get_or_create(user=request.user,job=job,tarket=tarket.profile,
        action="ส่งคำเชิญ",obj=job.title_th, defaults={})
    # Notifications.objects.create(user=request.user,job=job,tarket=tarket.profile,
    #     action="ส่งคำเชิญ",obj="สมัครงาน")

    status,created = InviteProcess.objects.get_or_create(disability=tarket,status="ส่งคำเชิญ",job=job, defaults={})

    return render(request, 'disable_detail.html', {'dis':tarket,'status':status.status})

def job_detail(request,job_name,job_id):
    # comp = CompanyInfo.objects.get(profile__user= request.user)

    job = Job.objects.get(title_th=job_name,id=job_id)
    company = job.company
    # company_image = Job
    status = "ยังไม่ส่งคำเชิญ"
    profile = Profile.objects.get(user=request.user)
    dis = DisabilityInfo.objects.get(profile=profile)
    job_qualification = ""
    qualification_list = job.qualification.split(",") 
    # for q in qualification_list:


    
    print(status,":status")
    if User.objects.filter(pk=request.user.id, groups__name='disability').exists() :
        
        try :

            invite = InviteProcess.objects.get(disability=dis,job=job) 
            status = invite.status

            print(status,":status")
            return render(request, 'job_detail.html', {'job':job,'status':status,'dis':dis.id})
        except :
            pass


    # print("info ",company)
    return render(request, 'job_detail.html', {'job':job,'company':company,'status':status,
        'dis':dis.id,'qualification_list':qualification_list})


def click_noti(request,job_name,job_id,noti_id):
    noti = Notifications.objects.get(id=noti_id)


    print(noti.is_read)
    if not noti.is_read :
        noti.is_read = True
        noti.save()
        # is_read.update(is_read=True)

    if User.objects.filter(pk=request.user.id, groups__name='disability').exists() :
 
        return job_detail(request,job_name,job_id)

    else :
        p = Profile.objects.get(user=noti.user)
        profile = DisabilityInfo.objects.get(profile=p)
        return disable_detail(request,profile.id,job_id)

def confirm_job(request,dis_id,job_id):
    job = Job.objects.get(id=job_id)
    InviteProcess.objects.filter(disability__id=dis_id,job__id=job_id).update(status="ตอบรับคำเชิญ")
    status = InviteProcess.objects.get(disability__id=dis_id,job__id=job_id)
    # return render(request, 'job_detail.html', {'job':job,'status':status.status})
    if User.objects.filter(pk=request.user.id, groups__name='company').exists() :
        dis = DisabilityInfo.objects.get(id=dis_id)
        Notifications.objects.get_or_create(user=request.user,job=job,tarket=dis.profile,
        action="ตอบรับคำเชิญ",obj=job.title_th, defaults={})
        return render(request, 'disable_detail.html', {'job':job,'status':status.status})
    else :
        Notifications.objects.get_or_create(user=request.user,job=job,tarket=job.company.profile,
        action="ตอบรับคำเชิญ",obj=job.title_th, defaults={})
        return render(request, 'job_detail.html', {'job':job,'status':status.status})

def show_notifications(request):
    list_noti =[]
    print("dothis")
    try :

        profile = Profile.objects.get(user=request.user)
        noti = Notifications.objects.filter(tarket=profile)
        for i in noti:
            
            temp = {'actor': '', 'action': '','target':'', 'obj':'','time':None,'img':None,
            'is_read': False,'job_id': None}
            
            if User.objects.filter(pk=request.user.id, groups__name='company').exists() :
                p = Profile.objects.get(user=i.user)
                dis = DisabilityInfo.objects.get(profile=p)
                temp['actor'] = dis.first_name
                temp['action'] = i.action
                temp['obj'] = i.obj
                temp['time'] = i.created_at
                temp['is_read'] = i.is_read
                temp['img'] = p.profile_picture.url
            else :
                p = Profile.objects.get(user=i.user)
                comp = CompanyInfo.objects.get(profile=p)
                temp['actor'] = comp.th_name
                temp['action'] = i.action
                temp['obj'] = i.obj
                temp['time'] = i.created_at
                temp['is_read'] = i.is_read
                temp['img'] = p.profile_picture.url

            list_noti.append(temp)


            
    except :
        raise

    print(list_noti,"555555")
    return render(request, 'notifications.html', {'list_noti':list_noti})

def apply_job(request,dis_id,job_id):
    job = Job.objects.get(id=job_id)
    Notifications.objects.get_or_create(user=request.user,job=job,tarket=job.company.profile,
        action="สมัครงาน",obj=job.title_th, defaults={})
    status,created = InviteProcess.objects.get_or_create(disability=DisabilityInfo.objects.get(id=dis_id),status="สมัครงาน",job=job, defaults={})
    return render(request, 'job_detail.html', {'job':job,'status':status.status})


def refuse_job(request,dis_id,job_id):
    job = Job.objects.get(id=job_id)
    dis = DisabilityInfo.objects.get(id=dis_id)
    Notifications.objects.get_or_create(user=request.user,job=job,tarket=dis.profile,
        action="ปฎิเสธงาน",obj=job.title_th, defaults={})
    status,created = InviteProcess.objects.get_or_create(disability=dis,status="ปฎิเสธงาน",job=job, defaults={})
    return render(request, 'job_detail.html', {'job':job,'status':status.status})


def contact(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'name.html', {'form': form})

def notification_mobile(request):
    list_noti =[]
    try :
     
        noti = Notifications.objects.filter(user=request.user)
        for i in noti:
            
            temp = {'name': '', 'action': '', 'obj':'','time':None,'img':None,'is_read': False}
            
            try :
                dis = CompanyInfo.objects.get(profile=i.tarket)

                temp['name'] = dis.th_name
                temp['action'] = i.action
                temp['obj'] = i.obj
                temp['time'] = i.created_at
                temp['is_read'] = i.is_read
                temp['img'] = i.tarket.profile_picture.url
                if temp['is_read'] == False and read:
                    read = False

              
                list_noti.append(temp)
            except :
                comp = DisabilityInfo.objects.get(profile=i.tarket)
                temp['name'] = comp.first_name
                temp['action'] = i.action
                temp['obj'] = i.obj
                temp['time'] = i.created_at
                temp['is_read'] = i.is_read
                temp['img'] = i.tarket.profile_picture.url
                if temp['is_read'] == False and read:
                    read = False

              
                list_noti.append(temp)

            
    except :
        raise
    return render(request, 'notification_mobile.html',{'noti':list_noti})

@login_required
def search(request):

    if request.user.groups.filter(name='company').exists():
        return redirect('employer_search')

    if request.method == 'POST':
        pass
    else :
        temp_dict = {}
        job_list = Job.objects.all()
        print(job_list)
        me = DisabilityInfo.objects.get(profile__user=request.user)

        south = ['จังหวัดกระบี่','จังหวัดชุมพร', 'จังหวัดตรัง', 'จังหวัดนครศรีธรรมราช' ,'จังหวัดนราธิวาส',
        'จังหวัดปัตตานี', 'จังหวัดพังงา', 'จังหวัดพัทลุง','จังหวัดภูเก็ต' ,'จังหวัดยะลา' ,'จังหวัดระนอง' ,
        'จังหวัดสงขลา', 'จังหวัดสตูล', 'จังหวัดสุราษฎร์ธานี']
        east = ['จังหวัดจันทบุรี', 'จังหวัดฉะเชิงเทรา' ,'จังหวัดชลบุรี' ,'จังหวัดตราด', 'จังหวัดปราจีนบุรี', 'จังหวัดระยอง' ,'จังหวัดสระแก้ว']
        west = ['จังหวัดกาญจนบุรี', 'จังหวัดตาก' ,'จังหวัดประจวบคีรีขันธ์','จังหวัดเพชรบุรี', 'จังหวัดราชบุรี']
        north = ['จังหวัดเชียงราย', 'จังหวัดเชียงใหม่' ,'จังหวัดน่าน', 'จังหวัดพะเยา', 'จังหวัดแพร่' ,'จังหวัดแม่ฮ่องสอน' ,'จังหวัดลำปาง', 'จังหวัดลำพูน', 'จังหวัดอุตรดิตถ์']
        north_east = ['กาฬสินธุ์', 'ขอนแก่น', 'ชัยภูมิ' ,'นครพนม' ,'นครราชสีมา' ,'บุรีรัมย์' ,'มหาสารคาม', 'มุกดาหาร',
        'ยโสธร', 'ร้อยเอ็ด','เลย', 'ศรีสะเกษ','สกลนคร' ,'สุรินทร์' ,'หนองคาย' ,'หนองบัวลำภู' ,'อำนาจเจริญ' ,
        'อุดรธานี','อุบลราชธานี' , 'บึงกาฬ']
        central = ['กรุงเทพมหานคร' ,'กำแพงเพชร', 'ชัยนาท' ,'นครนายก' ,'นครปฐม' ,'นครสวรรค์', 'นนทบุรี', 
        'ปทุมธานี', 'พระนครศรีอยุธยา' ,'พิจิตร' ,'พิษณุโลก','เพชรบูรณ์', 'ลพบุรี' ,'สมุทรปราการ', 'สมุทรสงคราม' ,
        'สมุทรสาคร' ,'สระบุรี' ,'สิงห์บุรี', 'สุโขทัย','สุพรรณบุรี', 'อ่างทอง', 'อุทัยธานี']

        zone = ""
        if me.province in north:
            zone = "ภาคเหนือ"
        elif me.province in north_east:
            zone = "ภาคตะวันออกเฉียงเหนือ"
        elif me.province in central:
            zone = "ภาคกลาง"
        elif me.province in east:
            zone = "ภาคตะวันออก"
        elif me.province in west:
            zone = "ภาคตะวันตก"

        # job_interest = me.job_interest
        the_string = me.job_interest
        myjob_interest_split = the_string.split(",")

        for job in job_list:
            score = 0
            company_zone = ""
            # lower_north_central_top = "สุโขทัย"
            # founded_province = False 
            # the_string = d.job_interest
            # j_split = the_string.split(",")

            if me.disability_cate in job.disability_cate:
                score +=20
            if me.province in job.province:
                score += 5
            else:
                if job.province in north:
                    company_zone = "ภาคเหนือ"
                elif job.province in north_east:
                    company_zone = "ภาคตะวันออกเฉียงเหนือ"
                elif job.province in central:
                    company_zone = "ภาคกลาง"
                elif job.province in east:
                    company_zone = "ภาคตะวันออก"
                elif job.province in west:
                    company_zone = "ภาคตะวันตก"           

                if zone == company_zone:
                    score +=5


            if me.sex in job.sex:
                score +=5

            for myjob in myjob_interest_split:
                
                seq = difflib.SequenceMatcher(None,job.title_th,myjob)
                percen = seq.ratio()*100
                print("percen ",percen)
                if percen >= 30.0:
                    score += 25
                elif percen>=10.0 and percen <=29.0:
                    score += 10
                elif percen < 10.0:
                    score+=0   
           
            qualification_list = job.qualification.split(",")
            for i in qualification_list:
                if i :
                    if me.talent in i or me.talent2 in i or me.talent3 in i:
                        score+=25
                        break

            if me.expected_salary1 <= job.salary1 or me.expected_salary1 <= job.salary2 :
                if me.expected_salary2 <= job.salary2:
                    score +=10
                elif me.expected_salary2 > job.salary2  :
                    score +=5
                else:
                    score +=5
            

            if me.age >= job.age1 and me.age <= job.age2 :
                score +=10
            elif  me.age >= job.age1 and me.age >= job.age2 :
                score +=5
            elif  me.age <= job.age1 :
                score +=5
            temp_dict[job.id] = score

        output_match = []
        temp_dict_reverse = sorted(temp_dict, key=temp_dict.get, reverse=True)
        print("temp_dict_reverse",temp_dict_reverse)   
        for r in temp_dict_reverse:
            temp={"job_id":0 ,"name":"","url_pic":None,"salary1":0,"salary2":0,
            "detail":"","dis_cate":"","province":"","score":0,"save":False}
            job_match = Job.objects.get(id=r)

            temp['score'] = temp_dict[r]
            temp['job_id'] = job_match.id
            temp['name'] = job_match.title_th
            temp['salary1'] = job_match.salary1
            temp['salary2'] = job_match.salary2
            temp['detail'] = job_match.detail
            temp['dis_cate'] = job_match.disability_cate
            temp['province'] = job_match.province
            c = CompanyInfo.objects.get(id=job_match.company.id)
            temp['url_pic'] =  Profile.objects.get(id=c.profile.id).profile_picture.url

            if Save.objects.filter(user=request.user,target=c.profile,name=job_match.title_th).exists():
                
                temp['save'] = True
            else:
                temp['save'] = False   
            output_match.append(temp)
        print (output_match)
        mysave = Save.objects.filter(user=request.user,)
        print("mysave",mysave)


        output_job = []
        for s in mysave:
            print("tar",s.target)
            print("name",s.name)
            temp_job ={"job_id":0 ,"job_name":"","company_image_url":None,"salary1":0,"salary2":0,
            "detail":"","dis_cate":"","province":"","score":0,"save":True}
             # {"job_name":None,"company_image_url":None}
            # company = Comp/anyInfo.objects.get(profile=s.target)
            # print(company)
            job = Job.objects.get(company__profile=s.target,title_th=s.name)
            print("job",job)
            temp_job["job_id"] = job.id
            temp_job["job_name"] = job.title_th
            temp_job["salary1"] = job.salary1
            temp_job["salary2"] = job.salary2
            temp_job["dis_cate"] = job.disability_cate
            temp_job["province"] = job.province
            temp_job['detail'] = job.detail
            temp_job["company_image_url"] = job.company.profile.profile_picture.url
            

            output_job.append(temp_job)
        profile = Profile.objects.get(user=request.user)
        invited = InviteProcess.objects.filter(disability__profile=profile)
        print("invited",invited)
        print("output_job",output_job)  




    return render(request, 'search.html',{'output_search':output_match,'output_job':output_job,'invited':invited})
  
@login_required
def employer_search(request):

  
    if request.user.groups.filter(name='disability').exists():
        return redirect('search')
     
    
    # dis_person = DisabilityInfo.objects.get(profile__user=request.user)

    if request.method == 'POST':
        print("ads")
        form = CreateJobForm(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            print("valid")
            company = CompanyInfo.objects.get(profile__user=request.user)
            age1 = 0
            age2 = 0 
            salary1 = 0
            salary2 = 0
            sex = ""
            if form.cleaned_data['sex'] == 0:
                sex = "ชาย"
            elif form.cleaned_data['sex'] == 1:
                sex = "หญิง"
            elif form.cleaned_data['sex'] == 2:
                sex = "หญิงชาย"    

            all_qualification = (form.cleaned_data['qualification']+','
                +form.cleaned_data['qualification2']+','+form.cleaned_data['qualification3']
                +','+form.cleaned_data['qualification4']+','+form.cleaned_data['qualification5']
                +','+form.cleaned_data['qualification6']+','+form.cleaned_data['qualification7']
                +','+form.cleaned_data['qualification8']
                +','+form.cleaned_data['qualification9']
                +','+form.cleaned_data['qualification10'])

            if form.cleaned_data['age1'] >= form.cleaned_data['age2'] :
                age2 = form.cleaned_data['age1']
                age1 = form.cleaned_data['age2']
            else :
                age1 = form.cleaned_data['age1']
                age2 = form.cleaned_data['age2']

            if form.cleaned_data['salary1'] >= form.cleaned_data['salary2'] :
                salary2 = form.cleaned_data['salary1']
                salary1 = form.cleaned_data['salary2']
            else :
                salary1 = form.cleaned_data['salary1']
                salary2 = form.cleaned_data['salary2']
                
            cj = Job.objects.create(
                company =company,
                title_th=form.cleaned_data['title_th'],
                title_en=form.cleaned_data['title_en'],
                email=form.cleaned_data['email'],
                phone_no=form.cleaned_data['phone_no'],
                age1 = age1,
                age2 = age2,
                sex =sex,
                detail = form.cleaned_data['job_detail'],
                disability_cate = form.cleaned_data['disability_type'],
                salary1 = salary1,
                salary2 = salary2,
                qualification = all_qualification,
                province=form.cleaned_data['province'],
                address=form.cleaned_data['location'],
           
                )
            print(cj)
            messages.success(request, "คุณได้สร้างประกาศงานเรียบร้อยแล้ว")
            print("คุณได้สร้างประกาศงานเรียบร้อยแล้ว")
            nextPage = "employer-search"
            return redirect(nextPage)


    else :
        temp_dict = {}
       
        company = CompanyInfo.objects.get(profile__user=request.user)
        try:
            job_declared = Job.objects.filter(company=company)
            job_title_th = ""
            for j in job_declared:
                job_title_th = j.title_th
                break
            job_required = Job.objects.get(title_th=job_title_th)     
        except Exception as e:
            return redirect('create_job')

        
       

       
        dis_list = DisabilityInfo.objects.all()
        print(dis_list)

        south = ['จังหวัดกระบี่','จังหวัดชุมพร', 'จังหวัดตรัง', 'จังหวัดนครศรีธรรมราช' ,'จังหวัดนราธิวาส',
        'จังหวัดปัตตานี', 'จังหวัดพังงา', 'จังหวัดพัทลุง','จังหวัดภูเก็ต' ,'จังหวัดยะลา' ,'จังหวัดระนอง' ,
        'จังหวัดสงขลา', 'จังหวัดสตูล', 'จังหวัดสุราษฎร์ธานี']
        east = ['จังหวัดจันทบุรี', 'จังหวัดฉะเชิงเทรา' ,'จังหวัดชลบุรี' ,'จังหวัดตราด', 'จังหวัดปราจีนบุรี', 'จังหวัดระยอง' ,'จังหวัดสระแก้ว']
        west = ['จังหวัดกาญจนบุรี', 'จังหวัดตาก' ,'จังหวัดประจวบคีรีขันธ์','จังหวัดเพชรบุรี', 'จังหวัดราชบุรี']
        north = ['จังหวัดเชียงราย', 'จังหวัดเชียงใหม่' ,'จังหวัดน่าน', 'จังหวัดพะเยา', 'จังหวัดแพร่' ,'จังหวัดแม่ฮ่องสอน' ,'จังหวัดลำปาง', 'จังหวัดลำพูน', 'จังหวัดอุตรดิตถ์']
        north_east = ['กาฬสินธุ์', 'ขอนแก่น', 'ชัยภูมิ' ,'นครพนม' ,'นครราชสีมา' ,'บุรีรัมย์' ,'มหาสารคาม', 'มุกดาหาร',
        'ยโสธร', 'ร้อยเอ็ด','เลย', 'ศรีสะเกษ','สกลนคร' ,'สุรินทร์' ,'หนองคาย' ,'หนองบัวลำภู' ,'อำนาจเจริญ' ,
        'อุดรธานี','อุบลราชธานี' , 'บึงกาฬ']
        central = ['กรุงเทพมหานคร' ,'กำแพงเพชร', 'ชัยนาท' ,'นครนายก' ,'นครปฐม' ,'นครสวรรค์', 'นนทบุรี', 
        'ปทุมธานี', 'พระนครศรีอยุธยา' ,'พิจิตร' ,'พิษณุโลก','เพชรบูรณ์', 'ลพบุรี' ,'สมุทรปราการ', 'สมุทรสงคราม' ,
        'สมุทรสาคร' ,'สระบุรี' ,'สิงห์บุรี', 'สุโขทัย','สุพรรณบุรี', 'อ่างทอง', 'อุทัยธานี']

        for d in dis_list:
            score = 0
            zone = ""
            dis_zone = ""
            # lower_north_central_top = "สุโขทัย"
            founded_province = False 
            the_string = d.job_interest
            j_split = the_string.split(",")

            if d.disability_cate in job_required.disability_cate:
                score +=20
            if d.province in job_required.province:
                score += 5
            else:
                if job_required.province in north:
                    zone = "ภาคเหนือ"
                elif job_required.province in north_east:
                    zone = "ภาคตะวันออกเฉียงเหนือ"
                elif job_required.province in central:
                    zone = "ภาคกลาง"
                elif job_required.province in east:
                    zone = "ภาคตะวันออก"
                elif job_required.province in west:
                    zone = "ภาคตะวันตก"           

                if d.province in north:
                    dis_zone = "ภาคเหนือ"
                elif d.province in north_east:
                    dis_zone = "ภาคตะวันออกเฉียงเหนือ"
                elif d.province in central:
                    dis_zone = "ภาคกลาง"
                elif d.province in east:
                    dis_zone = "ภาคตะวันออก"
                elif d.province in west:
                    dis_zone = "ภาคตะวันตก" 
                if zone == dis_zone:
                    score +=5
            for jl in j_split:
                
                seq = difflib.SequenceMatcher(None,job_required.title_th,jl)
                percen = seq.ratio()*100
                print("percen ",percen)
                if percen >= 30.0:
                    score += 25
                elif percen>=10.0 and percen <=29.0:
                    score += 5
                elif percen < 10.0:
                    score+=0   
            qualification_list = job_required.qualification.split(",")
            for i in qualification_list:
                if i :
                    if d.talent in i or  d.talent2 in i or d.talent3 in i:
                        score+=25
                        break




            if d.expected_salary1 <= job_required.salary1 or d.expected_salary1 <= job_required.salary2 :
                if d.expected_salary2 <= job_required.salary2:
                    score +=10
                elif d.expected_salary2 > job_required.salary2  :
                    score +=5
                else:
                    score +=5
            if d.sex in job_required.sex:
                score +=5        

            if d.age >= job_required.age1 and d.age <= job_required.age2 :
                score +=10
            elif  d.age >= job_required.age1 and d.age >= job_required.age2 :
                score +=5
            elif  d.age <= job_required.age1 :
                score +=5

            # print (score)
            temp_dict[d.id] = score
        output_match = []
        temp_dict_reverse = sorted(temp_dict, key=temp_dict.get, reverse=True)
        print("temp_dict_reverse",temp_dict_reverse)   
        for r in temp_dict_reverse:
            temp={"id":0,"name":"","job_interest":"","url_pic":None,"expected_salary1":0,"expected_salary2":0,
            "job_exp":"","dis_cate":"","province":"","score":0,"save":False}
            dis = DisabilityInfo.objects.get(id=r)
            temp['id'] = dis.id 
            temp['score'] = temp_dict[r]
            temp['name'] = dis.first_name+" "+dis.last_name
            temp['job_interest'] = dis.job_interest
            temp['expected_salary1'] = dis.expected_salary1
            temp['expected_salary2'] = dis.expected_salary2
            temp['job_exp'] = dis.job_exp
            temp['dis_cate'] = dis.disability_cate
            temp['province'] = dis.province
            temp['url_pic'] = Profile.objects.get(id=dis.profile.id).profile_picture.url
            name =dis.first_name+" "+dis.last_name
            try:
                s = Save.objects.get(user=request.user,target=dis.profile,name=name)
                temp['save'] = True
                print("save")

            except Exception as e:
                temp['save'] = False
        
           
                
            



            output_match.append(temp)
        # print (output)
            # output_match.append(temp)
        print (output_match)


        form = CreateJobForm()

        return render(request, 'employer_search.html',{'form':form,'job_declared':job_declared,'output':output_match,'job_id':job_required.id})


def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			email= form.cleaned_data.get('email')
			name = form.cleaned_data.get('name')
			phone= form.cleaned_data.get('phone')
			subject = form.cleaned_data.get('subject')
			message= form.cleaned_data.get('message')
			status = True

			Contact.objects.create(email=email,name=name,phone=phone,subject=subject,message=message)

		return render(request, 'contact.html',{'username': request.user.username,'form':form,'status':status})



	else :
		form = ContactForm()
	return render(request, 'contact.html',{'username': request.user.username,'form':form})
  
@login_required
def employer_search_disability(request):
    company = CompanyInfo.objects.get(profile__user=request.user)
    job_declared = Job.objects.filter(company=company)
    if request.method == 'POST':
        job_title_th = request.POST['selectJob']
        temp_dict = {}
        temp_dict2 = {}
   
        job_required = Job.objects.get(title_th=job_title_th) 
        dis_list = DisabilityInfo.objects.all()
        print(dis_list)

        south = ['จังหวัดกระบี่','จังหวัดชุมพร', 'จังหวัดตรัง', 'จังหวัดนครศรีธรรมราช' ,'จังหวัดนราธิวาส',
        'จังหวัดปัตตานี', 'จังหวัดพังงา', 'จังหวัดพัทลุง','จังหวัดภูเก็ต' ,'จังหวัดยะลา' ,'จังหวัดระนอง' ,
        'จังหวัดสงขลา', 'จังหวัดสตูล', 'จังหวัดสุราษฎร์ธานี']
        east = ['จังหวัดจันทบุรี', 'จังหวัดฉะเชิงเทรา' ,'จังหวัดชลบุรี' ,'จังหวัดตราด', 'จังหวัดปราจีนบุรี', 'จังหวัดระยอง' ,'จังหวัดสระแก้ว']
        west = ['จังหวัดกาญจนบุรี', 'จังหวัดตาก' ,'จังหวัดประจวบคีรีขันธ์','จังหวัดเพชรบุรี', 'จังหวัดราชบุรี']
        north = ['จังหวัดเชียงราย', 'จังหวัดเชียงใหม่' ,'จังหวัดน่าน', 'จังหวัดพะเยา', 'จังหวัดแพร่' ,'จังหวัดแม่ฮ่องสอน' ,'จังหวัดลำปาง', 'จังหวัดลำพูน', 'จังหวัดอุตรดิตถ์']
        north_east = ['กาฬสินธุ์', 'ขอนแก่น', 'ชัยภูมิ' ,'นครพนม' ,'นครราชสีมา' ,'บุรีรัมย์' ,'มหาสารคาม', 'มุกดาหาร',
        'ยโสธร', 'ร้อยเอ็ด','เลย', 'ศรีสะเกษ','สกลนคร' ,'สุรินทร์' ,'หนองคาย' ,'หนองบัวลำภู' ,'อำนาจเจริญ' ,
        'อุดรธานี','อุบลราชธานี' , 'บึงกาฬ']
        central = ['กรุงเทพมหานคร' ,'กำแพงเพชร', 'ชัยนาท' ,'นครนายก' ,'นครปฐม' ,'นครสวรรค์', 'นนทบุรี', 
        'ปทุมธานี', 'พระนครศรีอยุธยา' ,'พิจิตร' ,'พิษณุโลก','เพชรบูรณ์', 'ลพบุรี' ,'สมุทรปราการ', 'สมุทรสงคราม' ,
        'สมุทรสาคร' ,'สระบุรี' ,'สิงห์บุรี', 'สุโขทัย','สุพรรณบุรี', 'อ่างทอง', 'อุทัยธานี']

        for d in dis_list:
            score = 0
            zone = ""
            dis_zone = ""
            # lower_north_central_top = "สุโขทัย"
            founded_province = False 
            the_string = d.job_interest
            j_split = the_string.split(",")

            if d.disability_cate in job_required.disability_cate:
                score +=20
            if d.province in job_required.province:
                score += 5
            else:
                if job_required.province in north:
                    zone = "ภาคเหนือ"
                elif job_required.province in north_east:
                    zone = "ภาคตะวันออกเฉียงเหนือ"
                elif job_required.province in central:
                    zone = "ภาคกลาง"
                elif job_required.province in east:
                    zone = "ภาคตะวันออก"
                elif job_required.province in west:
                    zone = "ภาคตะวันตก"           

                if d.province in north:
                    dis_zone = "ภาคเหนือ"
                elif d.province in north_east:
                    dis_zone = "ภาคตะวันออกเฉียงเหนือ"
                elif d.province in central:
                    dis_zone = "ภาคกลาง"
                elif d.province in east:
                    dis_zone = "ภาคตะวันออก"
                elif d.province in west:
                    dis_zone = "ภาคตะวันตก" 
                if zone == dis_zone:
                    score +=5
            for jl in j_split:
                
                seq = difflib.SequenceMatcher(None,job_required.title_th,jl)
                percen = seq.ratio()*100
                print("percen ",percen)
                if percen >= 30.0:
                    score += 25
                elif percen>=10.0 and percen <=29.0:
                    score += 5
                elif percen < 10.0:
                    score+=0   
            qualification_list = job_required.qualification.split(",")
            for i in qualification_list:
                if i :
                    if d.talent in i or  d.talent2 in i or d.talent3 in i:
                        score+=25
                        break




            if d.expected_salary1 <= job_required.salary1 or d.expected_salary1 <= job_required.salary2 :
                if d.expected_salary2 <= job_required.salary2:
                    score +=10
                elif d.expected_salary2 > job_required.salary2  :
                    score +=5
                else:
                    score +=5
            if d.sex in job_required.sex:
                score +=5        

            if d.age >= job_required.age1 and d.age <= job_required.age2 :
                score +=10
            elif  d.age >= job_required.age1 and d.age >= job_required.age2 :
                score +=5
            elif  d.age <= job_required.age1 :
                score +=5


            # print (score)
            temp_dict[d.id] = score
        output = []
        temp_dict_reverse = sorted(temp_dict, key=temp_dict.get, reverse=True)
        # print("temp_dict_reverse",temp_dict_reverse)   
        for r in temp_dict_reverse:
            temp={"id":0,"name":"","job_interest":"","url_pic":None,"expected_salary1":0,"expected_salary2":0,
            "job_exp":"","dis_cate":"","province":"","score":0,'save':False}
            dis = DisabilityInfo.objects.get(id=r)
            temp['id'] = dis.id 
            temp['score'] = temp_dict[r]
            temp['name'] = dis.first_name+" "+dis.last_name
            temp['job_interest'] = dis.job_interest
            temp['expected_salary1'] = dis.expected_salary1
            temp['expected_salary2'] = dis.expected_salary2
            temp['job_exp'] = dis.job_exp
            temp['dis_cate'] = dis.disability_cate
            temp['province'] = dis.province
            temp['url_pic'] = Profile.objects.get(id=dis.profile.id).profile_picture.url
            name =dis.first_name+" "+dis.last_name
            try:
                s = Save.objects.get(user=request.user,target=dis.profile,name=name)
                temp['save'] = True
             
            except Exception as e:
                temp['save'] = False
        
            output.append(temp)
        # print (output)
        return render(request, 'employer_search.html',{'output':output,'job_declared':job_declared,'job_title_th':job_title_th,'job_id':job_required.id})

@login_required
def disable_search_job(request):
    job_title_th = request.GET.get('job_title',"")
    dis_cate = request.GET.get('dis_cate',"")
    location = request.GET.get('location',"")
    salary1 = request.GET.get('salary1',"")
    salary2 = request.GET.get('salary2',"")

    if salary1 is "" or salary2 is "":
        search_job_list = Job.objects.filter(
        Q(title_th__icontains=job_title_th),
        Q(province__icontains=location),
        Q(disability_cate__icontains=dis_cate),
        )
    else:
        search_job_list = Job.objects.filter(
        Q(title_th__icontains=job_title_th),
        Q(province__icontains=location),
        Q(disability_cate__icontains=dis_cate),
        Q(salary1__gte=salary1) | Q(salary1__lte=salary2) & Q(salary2__lte=salary2),
        )
    output =[]
    for i in search_job_list:
        temp={"id":0,"name":"","detail":"","url_pic":None,"salary1":0,"salary2":0,
            "job_exp":"","dis_cate":"","province":"","save":False}
        temp['id'] = i.id         
        temp['name'] = i.title_th
        temp['detail'] = i.detail
        temp['salary1'] = i.salary1
        temp['salary2'] = i.salary2
        temp['dis_cate'] = i.disability_cate
        temp['province'] = i.province
        temp['url_pic'] = i.company.profile.profile_picture.url
        c = CompanyInfo.objects.get(id=i.company.id)
        try:
            s = Save.objects.get(user=request.user,target=c.profile,name=i.title_th)
            temp['save'] = True
            print("<savetrue></savetrue>")

        except Exception as e:
            temp['save'] = False

        output.append(temp)
    
    print("type",type(salary2))
    print("job_title_th",job_title_th)
    print("searcj",search_job_list)
    mysave = Save.objects.filter(user=request.user,)
    print("mysave",mysave)


    output_job = []
    for s in mysave:
        print("tar",s.target)
        print("name",s.name)
        temp_job ={"job_id":0 ,"job_name":"","company_image_url":None,"salary1":0,"salary2":0,
        "detail":"","dis_cate":"","province":"","score":0,"save":True}
             # {"job_name":None,"company_image_url":None}
            # company = Comp/anyInfo.objects.get(profile=s.target)
            # print(company)
        job = Job.objects.get(company__profile=s.target,title_th=s.name)
        print("job",job)
        temp_job["job_id"] = job.id
        temp_job["job_name"] = job.title_th
        temp_job["salary1"] = job.salary1
        temp_job["salary2"] = job.salary2
        temp_job["dis_cate"] = job.disability_cate
        temp_job["province"] = job.province
        temp_job['detail'] = job.detail
        temp_job["company_image_url"] = job.company.profile.profile_picture.url
            

        output_job.append(temp_job)
        profile = Profile.objects.get(user=request.user)
        invited = InviteProcess.objects.filter(disability__profile=profile)
        print("invited",invited)
        print("output_job",output_job) 

    return render(request, 'search.html',{'search_job_list':output,
        'job_title_th':job_title_th,'dis_cate':dis_cate,'location':location,
        'salary1':salary1,'salary2':salary2,'output_job':output_job,'invited':invited})


@login_required
def company_save_disable(request):
    print("in checkIsSell")
    if request.method == 'POST':
        print("in post")
        # user = request.user
        dis_id = request.POST.get('dis_id', None)
        title = request.POST.get('title', None)

        print(title)
        dis =DisabilityInfo.objects.get(id=dis_id)
        name =dis.first_name+" "+dis.last_name
        print(dis)
        # print(isChecked)
        if title == 'บันทึก':
            Save.objects.create(user=request.user,target=dis.profile,name=name)
            context = 'create'
            print("create")
        else:
            Save.objects.filter(user=request.user,target=dis.profile,name=name).delete()
            print("delete")
            context = 'delete'

    
    return HttpResponse(json.dumps(context), content_type='application/json')

@login_required
def disable_save_job(request):
    print("in checkIsSell")
    if request.method == 'POST':
        print("in post")
        # user = request.user
        job_id = request.POST.get('job_id', None)
        title = request.POST.get('title', None)

        print(title)
        job =Job.objects.get(id=job_id)
        # profile = Profile.objects.get(company=job.company)
        print(job)
        # print(isChecked)
        if title == 'บันทึก':
            Save.objects.create(user=request.user,target=job.company.profile,name=job.title_th)
            context = 'create'
        else:
            Save.objects.filter(user=request.user,target=job.company.profile,name=job.title_th).delete()
            print("delete")
            context = 'delete'

    
    return HttpResponse(json.dumps(context), content_type='application/json')

def create_job(request):
    if request.method == 'POST':
        form = CreateJobForm(request.POST, request.FILES)
        if form.is_valid():
            print("valid")
            company = CompanyInfo.objects.get(profile__user=request.user)
            age1 = 0
            age2 = 0 
            salary1 = 0
            salary2 = 0
            sex = ""
            if form.cleaned_data['sex'] == 0:
                sex = "ชาย"
            elif form.cleaned_data['sex'] == 1:
                sex = "หญิง"
            elif form.cleaned_data['sex'] == 2:
                sex = "หญิงชาย"    

            all_qualification = (form.cleaned_data['qualification']+','
                +form.cleaned_data['qualification2']+','+form.cleaned_data['qualification3']
                +','+form.cleaned_data['qualification4']+','+form.cleaned_data['qualification5']
                +','+form.cleaned_data['qualification6']+','+form.cleaned_data['qualification7']
                +','+form.cleaned_data['qualification8']
                +','+form.cleaned_data['qualification9']
                +','+form.cleaned_data['qualification10'])

            if form.cleaned_data['age1'] >= form.cleaned_data['age2'] :
                age2 = form.cleaned_data['age1']
                age1 = form.cleaned_data['age2']
            else :
                age1 = form.cleaned_data['age1']
                age2 = form.cleaned_data['age2']

            if form.cleaned_data['salary1'] >= form.cleaned_data['salary2'] :
                salary2 = form.cleaned_data['salary1']
                salary1 = form.cleaned_data['salary2']
            else :
                salary1 = form.cleaned_data['salary1']
                salary2 = form.cleaned_data['salary2']
                
            cj = Job.objects.create(
                company =company,
                title_th=form.cleaned_data['title_th'],
                title_en=form.cleaned_data['title_en'],
                email=form.cleaned_data['email'],
                phone_no=form.cleaned_data['phone_no'],
                age1 = age1,
                age2 = age2,
                sex =sex,
                detail = form.cleaned_data['job_detail'],
                disability_cate = form.cleaned_data['disability_type'],
                salary1 = salary1,
                salary2 = salary2,
                qualification = all_qualification,
                province=form.cleaned_data['province'],
                address=form.cleaned_data['location'],
           
                )
            print(cj)
            messages.success(request, "คุณได้สร้างประกาศงานเรียบร้อยแล้ว")
            print("คุณได้สร้างประกาศงานเรียบร้อยแล้ว")
            return redirect("employer-search")


    else :
        form = CreateJobForm()
    return render(request, 'create_job.html',{'form':form})

# 'job_declared':job_declared,'job_title_th':job_title_th
    # company = CompanyInfo.objects.get(profile__user=request.user)
    # job_declared = Job.objects.filter(company=company)
    # if request.method == 'POST':
    #     job_title_th = request.POST['job_title'],
    #     dis_cate = request.POST['disability_type']
    #     location = request.POST['location']
    #     salary1 = request.POST['salary1']
    #     salary2 = request.POST['salary2']

    #     temp_dict = {}
    #     job_list = Job.objects.all()
       
    #     me = DisabilityInfo.objects.get(profile__user=request.user)

    #     south = ['จังหวัดกระบี่','จังหวัดชุมพร', 'จังหวัดตรัง', 'จังหวัดนครศรีธรรมราช' ,'จังหวัดนราธิวาส',
    #     'จังหวัดปัตตานี', 'จังหวัดพังงา', 'จังหวัดพัทลุง','จังหวัดภูเก็ต' ,'จังหวัดยะลา' ,'จังหวัดระนอง' ,
    #     'จังหวัดสงขลา', 'จังหวัดสตูล', 'จังหวัดสุราษฎร์ธานี']
    #     east = ['จังหวัดจันทบุรี', 'จังหวัดฉะเชิงเทรา' ,'จังหวัดชลบุรี' ,'จังหวัดตราด', 'จังหวัดปราจีนบุรี', 'จังหวัดระยอง' ,'จังหวัดสระแก้ว']
    #     west = ['จังหวัดกาญจนบุรี', 'จังหวัดตาก' ,'จังหวัดประจวบคีรีขันธ์','จังหวัดเพชรบุรี', 'จังหวัดราชบุรี']
    #     north = ['จังหวัดเชียงราย', 'จังหวัดเชียงใหม่' ,'จังหวัดน่าน', 'จังหวัดพะเยา', 'จังหวัดแพร่' ,'จังหวัดแม่ฮ่องสอน' ,'จังหวัดลำปาง', 'จังหวัดลำพูน', 'จังหวัดอุตรดิตถ์']
    #     north_east = ['กาฬสินธุ์', 'ขอนแก่น', 'ชัยภูมิ' ,'นครพนม' ,'นครราชสีมา' ,'บุรีรัมย์' ,'มหาสารคาม', 'มุกดาหาร',
    #     'ยโสธร', 'ร้อยเอ็ด','เลย', 'ศรีสะเกษ','สกลนคร' ,'สุรินทร์' ,'หนองคาย' ,'หนองบัวลำภู' ,'อำนาจเจริญ' ,
    #     'อุดรธานี','อุบลราชธานี' , 'บึงกาฬ']
    #     central = ['กรุงเทพมหานคร' ,'กำแพงเพชร', 'ชัยนาท' ,'นครนายก' ,'นครปฐม' ,'นครสวรรค์', 'นนทบุรี', 
    #     'ปทุมธานี', 'พระนครศรีอยุธยา' ,'พิจิตร' ,'พิษณุโลก','เพชรบูรณ์', 'ลพบุรี' ,'สมุทรปราการ', 'สมุทรสงคราม' ,
    #     'สมุทรสาคร' ,'สระบุรี' ,'สิงห์บุรี', 'สุโขทัย','สุพรรณบุรี', 'อ่างทอง', 'อุทัยธานี']
    #     search_job = 
        # zone = ""
        # if me.province in north:
        #     zone = "ภาคเหนือ"
        # elif me.province in north_east:
        #     zone = "ภาคตะวันออกเฉียงเหนือ"
        # elif me.province in central:
        #     zone = "ภาคกลาง"
        # elif me.province in east:
        #     zone = "ภาคตะวันออก"
        # elif me.province in west:
        #     zone = "ภาคตะวันตก"

        # job_interest = me.job_interest
        # the_string = me.job_interest
        # myjob_interest_split = the_string.split(",")

        # for job in job_list:
        #     score = 0
        #     company_zone = ""
            # lower_north_central_top = "สุโขทัย"
            # founded_province = False 
            # the_string = d.job_interest
            # j_split = the_string.split(",")

            # if me.disability_cate in dis_cate:
            #     score +=20
            # if me.province in location:
            #     score += 20
            # else:
            #     if location in north:
            #         company_zone = "ภาคเหนือ"
            #     elif location in north_east:
            #         company_zone = "ภาคตะวันออกเฉียงเหนือ"
            #     elif location in central:
            #         company_zone = "ภาคกลาง"
            #     elif location in east:
            #         company_zone = "ภาคตะวันออก"
            #     elif location in west:
            #         company_zone = "ภาคตะวันตก"           

            #     if zone == company_zone:
            #         score +=10

            # for myjob in myjob_interest_split:
                
            #     seq = difflib.SequenceMatcher(None,job.title_th,myjob)
            #     percen = seq.ratio()*100
            #     print("percen ",percen)
            #     if percen >= 30.0:
            #         score += 20
            #     elif percen>=10.0 and percen <=29.0:
            #         score += 10
            #     elif percen < 10.0:
            #         score+=0   
           

            # if me.expected_salary1 <= salary1 or me.expected_salary1 <= salary2 :
            #     if me.expected_salary2 <= salary2:
            #         score +=20
            #     elif me.expected_salary2 > salary2  :
            #         score +=15
            #     else:
            #         score +=15
                     

            # if me.age >= job.age1 and me.age <= job.age2 :
            #     score +=20
            # elif  me.age >= job.age1 and me.age >= job.age2 :
            #     score +=5
            # elif  me.age <= job.age1 :
            #     score +=5
            # temp_dict[job.id] = score

        # output_match = []
        # temp_dict_reverse = sorted(temp_dict, key=temp_dict.get, reverse=True)
        # print("temp_dict_reverse",temp_dict_reverse)   
        # for r in temp_dict_reverse:
        #     temp={"name":"","url_pic":None,"expected_salary1":0,"expected_salary2":0,
        #     "job_exp":"","dis_cate":"","province":"","score":0}
        #     job_match = Job.objects.get(id=r)

        #     temp['score'] = temp_dict[r]
        #     temp['name'] = job_match.title_th
        #     # temp['job_interest'] = dis.job_interest
        #     temp['salary1'] = job_match.salary1
        #     temp['salary12'] = job_match.salary2
        #     temp['job_exp'] = job_match.detail
        #     temp['dis_cate'] = job_match.disability_cate
        #     temp['province'] = job_match.province
        #     c = CompanyInfo.objects.get(id=job_match.company.id)
        #     # print("cid",c.profile.id)
        #     temp['url_pic'] =  Profile.objects.get(id=c.profile.id).profile_picture.url
        #     output_match.append(temp)
        # print (output)
            # output_match.append(temp)
        # print (output_match)

    # return render(request, 'employer_search.html',)
    # print("temp_dict2",temp_dict2)
    # for key, value in temp_dict2.items():
    #     print ("key "+str(key)+" value "+str(value))

  
            # if d.province in north:



            # for pn in north:
            #     if d.province in pn:
            #         founded_province = True
            #         score +=20
            #         break
            # if not founded_province:
            #     for ps in south:
            #         pass
            
            # for pe in east:
            #     pass
            
            # pak
       

     

    # print("s1 ",job_required.salary1)

    # disability_list = DisabilityInfo.objects.filter(
    # Q(province__icontains=job_required.province),
    # Q(disability_cate__icontains=job_required.disability_cate),
    # Q(job_interest__icontains=job_required.qulification),
    # Q(expected_salary1__gte=job_required.salary1) | Q(expected_salary1__lte=job_required.salary2) & Q(expected_salary2__lte=job_required.salary2),
    # )

    # # dis_list = DisabilityInfo.objects.filter(address__icontains=job_required.traveling)
    # dis_list = DisabilityInfo.objects.filter(address__icontains=job_required.traveling)

    # for dis in disability_list:
    #     print(dis.expected_salary1)
    #     print(dis.expected_salary2)
    # print(job_required)
    # pass
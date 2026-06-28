from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Component, PCBuild

def landing_view(request):
    return render(request, 'configurator/landing.html')

def index_view(request):
    if Component.objects.count() < 15:
        Component.objects.all().delete()
        Component.objects.bulk_create([
            Component(name="Core i9-14900K", category="CPU", brand="Intel", price=549.00, wattage=125),
            Component(name="Core i7-14700K", category="CPU", brand="Intel", price=409.00, wattage=125),
            Component(name="Core i5-14600K", category="CPU", brand="Intel", price=299.00, wattage=125),
            Component(name="Ryzen 9 7950X3D", category="CPU", brand="AMD", price=599.00, wattage=120),
            Component(name="Ryzen 7 7800X3D", category="CPU", brand="AMD", price=389.00, wattage=120),
            Component(name="Ryzen 5 7600X", category="CPU", brand="AMD", price=219.00, wattage=105),
            Component(name="GeForce RTX 4090 ROG Strix", category="GPU", brand="NVIDIA", price=1999.00, wattage=450),
            Component(name="GeForce RTX 4080 Super", category="GPU", brand="NVIDIA", price=999.00, wattage=320),
            Component(name="GeForce RTX 4070 Super", category="GPU", brand="NVIDIA", price=599.00, wattage=220),
            Component(name="ROG STRIX Z790-E GAMING WIFI", category="MOBO", brand="ASUS", price=360.00, wattage=50),
            Component(name="B650 AORUS ELITE AX", category="MOBO", brand="GIGABYTE", price=219.00, wattage=45),
            Component(name="Vengeance RGB 32GB DDR5 6000MHz", category="RAM", brand="Corsair", price=125.00, wattage=15),
            Component(name="Fury Beast RGB 16GB DDR5 5600MHz", category="Kingston", price=75.00, wattage=12),
            Component(name="990 PRO NVMe M.2 2TB", category="SSD", brand="Samsung", price=169.00, wattage=8),
            Component(name="RM850x 850W 80+ Gold", category="PSU", brand="Corsair", price=134.00, wattage=0),
        ])

    if 'selected_components' not in request.session:
        request.session['selected_components'] = []

    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    components = Component.objects.all()
    if category_filter:
        components = components.filter(category=category_filter)
    if search_query:
        components = components.filter(name__icontains=search_query) | components.filter(brand__icontains=search_query)

    selected_ids = request.session['selected_components']
    selected_components = Component.objects.filter(id__in=selected_ids)
    
    total_price = sum(c.price for c in selected_components)
    total_wattage = sum(c.wattage for c in selected_components)
    
    build_image = "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=600&q=80"
    if selected_components.exists():
        if selected_components.filter(price__gte=400).exists():
            build_image = "https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?auto=format&fit=crop&w=600&q=80"
        elif selected_components.filter(category='GPU').exists():
            build_image = "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=600&q=80"

    warning_message = ""
    has_psu = selected_components.filter(category='PSU').exists()
    if total_wattage > 0 and not has_psu:
        warning_message = "⚠️ სისტემას სჭირდება კვების ბლოკი (PSU)!"

    has_cpu = selected_components.filter(category='CPU').first()
    has_gpu = selected_components.filter(category='GPU').first()
    has_mobo = selected_components.filter(category='MOBO').first()
    
    bottleneck_message = ""
    compatibility_error = ""
    fps_data = None

    # ---- SOCKET CHECK ----
    if has_cpu and has_mobo:
        cpu_socket = "LGA1700" if has_cpu.brand.lower() == "intel" else "AM5"
        mobo_socket = "LGA1700" if "z790" in has_mobo.name.lower() else "AM5"
        if cpu_socket != mobo_socket:
            compatibility_error = f"❌ თავსებადობის შეცდომა: პროცესორი იყენებს {cpu_socket} სოკეტს, ხოლო დედაპლატა {mobo_socket}-ს!"

    # ---- BOTTLENECK & FPS ----
    if has_cpu and has_gpu:
        if has_gpu.price >= 900 and has_cpu.price < 300:
            bottleneck_message = "⚠️ Bottleneck Alert: პროცესორი შეაფერხებს ვიდეობარათს!"
        
        gpu_name = has_gpu.name.lower()
        if "4090" in gpu_name:
            fps_data = {"cs2": "500+ FPS", "cyberpunk": "120+ (2K)", "gta5": "240+ FPS"}
        elif "4080" in gpu_name:
            fps_data = {"cs2": "420+ FPS", "cyberpunk": "95+ (2K)", "gta5": "190+ FPS"}
        else:
            fps_data = {"cs2": "360+ FPS", "cyberpunk": "85+ (2K)", "gta5": "160+ FPS"}

    # ---- 📊 BUILD SCORE & TIER ----
    build_score = 0
    build_tier = "ცარიელი"
    if selected_components.exists():
        build_score = min(100, int(30 + (total_price / 35)))
        if bottleneck_message:
            build_score = max(15, build_score - 20)
        if compatibility_error:
            build_score = 0
            
        if total_price < 800:
            build_tier = "ბიუჯეტური (Entry-Level) 💻"
        elif total_price < 1600:
            build_tier = "საშუალო (Mid-Range Gaming) 2K 🎮"
        elif total_price < 2800:
            build_tier = "მაღალი (High-End Beast) 🔥"
        else:
            build_tier = "ულტრა (Enthusiast Monster) 🚀"

    all_builds = PCBuild.objects.all().order_by('-created_at')

    context = {
        'components': components,
        'selected_components': selected_components,
        'total_price': total_price,
        'total_wattage': total_wattage,
        'warning_message': warning_message,
        'bottleneck_message': bottleneck_message,
        'compatibility_error': compatibility_error,
        'fps_data': fps_data,
        'build_score': build_score,
        'build_tier': build_tier,
        'all_builds': all_builds,
        'categories': Component.CATEGORY_CHOICES,
        'selected_category': category_filter,
        'search_query': search_query,
        'build_image': build_image,
    }
    return render(request, 'configurator/index.html', context)

def toggle_component(request, comp_id):
    if 'selected_components' not in request.session:
        request.session['selected_components'] = []
    selected = request.session['selected_components']
    if comp_id in selected:
        selected.remove(comp_id)
    else:
        selected.append(comp_id)
    request.session['selected_components'] = selected
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def save_build(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        selected_ids = request.session.get('selected_components', [])
        if selected_ids and title:
            build = PCBuild.objects.create(title=title, creator=request.user)
            components = Component.objects.filter(id__in=selected_ids)
            build.components.set(components)
            request.session['selected_components'] = []
            messages.success(request, "ბილდი წარმატებით შეინახა!")
    return redirect('index')

# ---- 🔐 AUTHENTICATION VIEWS ----
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "რეგისტრაცია წარმატებით გაიარეთ!")
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'configurator/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "წარმატებით შეხვედით სისტემაში!")
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'configurator/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "სისტემიდან გამოხვედით!")
    return redirect('landing')

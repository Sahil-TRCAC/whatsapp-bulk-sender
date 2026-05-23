from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Contact, ContactGroup
from .forms import ContactForm, ContactGroupForm, ContactImportForm
import pandas as pd
import io
import re


@login_required
def contact_list(request):
    contacts = Contact.objects.filter(user=request.user)
    search = request.GET.get('search', '')
    if search:
        contacts = contacts.filter(name__icontains=search) | contacts.filter(phone__icontains=search)
    
    paginator = Paginator(contacts, 20)
    page = request.GET.get('page', 1)
    contacts_page = paginator.get_page(page)
    
    return render(request, 'contacts/list.html', {
        'contacts': contacts_page,
        'search': search,
    })


@login_required
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            if request.POST.get('groups'):
                contact.groups.set(request.POST.getlist('groups'))
            messages.success(request, 'Contact created successfully!')
            return redirect('contact_list')
    else:
        form = ContactForm()
        groups = ContactGroup.objects.filter(user=request.user)
    return render(request, 'contacts/form.html', {'form': form, 'groups': groups})


@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            if request.POST.get('groups'):
                contact.groups.set(request.POST.getlist('groups'))
            messages.success(request, 'Contact updated successfully!')
            return redirect('contact_list')
    else:
        form = ContactForm(instance=contact)
        groups = ContactGroup.objects.filter(user=request.user)
    return render(request, 'contacts/form.html', {'form': form, 'groups': groups, 'contact': contact})


@require_POST
@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    contact.delete()
    messages.success(request, 'Contact deleted successfully!')
    return redirect('contact_list')


@login_required
def contact_import(request):
    if request.method == 'POST':
        form = ContactImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                required_cols = ['name', 'phone']
                if not all(col in df.columns for col in required_cols):
                    messages.error(request, 'File must have columns: name, phone')
                    return redirect('contact_import')
                
                count = 0
                for _, row in df.iterrows():
                    name = str(row.get('name', '')).strip()
                    phone = str(row.get('phone', '')).strip()
                    if name and phone:
                        phone = re.sub(r'\D', '', phone)
                        if not phone.startswith('+'):
                            phone = '+' + phone
                        Contact.objects.get_or_create(
                            user=request.user,
                            phone=phone,
                            defaults={'name': name}
                        )
                        count += 1
                
                messages.success(request, f'Imported {count} contacts successfully!')
                return redirect('contact_list')
            except Exception as e:
                messages.error(request, f'Error importing file: {str(e)}')
    else:
        form = ContactImportForm()
    return render(request, 'contacts/import.html', {'form': form})


@login_required
def group_list(request):
    groups = ContactGroup.objects.filter(user=request.user)
    return render(request, 'contacts/groups.html', {'groups': groups})


@login_required
def group_create(request):
    if request.method == 'POST':
        form = ContactGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.user = request.user
            group.save()
            messages.success(request, 'Group created successfully!')
            return redirect('group_list')
    else:
        form = ContactGroupForm()
    return render(request, 'contacts/group_form.html', {'form': form})


@login_required
def group_edit(request, pk):
    group = get_object_or_404(ContactGroup, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ContactGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated successfully!')
            return redirect('group_list')
    else:
        form = ContactGroupForm(instance=group)
    return render(request, 'contacts/group_form.html', {'form': form, 'group': group})


@require_POST
@login_required
def group_delete(request, pk):
    group = get_object_or_404(ContactGroup, pk=pk, user=request.user)
    group.delete()
    messages.success(request, 'Group deleted successfully!')
    return redirect('group_list')
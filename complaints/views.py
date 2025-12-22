from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone

from .models import Complaint, Image
from .forms import ComplaintCreateForm, ComplaintAdminUpdateForm, ComplaintModeratorUpdateForm, TashkilotForm, UserCreateForm
from common.models import Region, District, Tashkilot
from users.models import CustomUser


# ============================================================================
# MIXINS FOR ROLE-BASED ACCESS CONTROL
# ============================================================================

class UserRoleMixin(UserPassesTestMixin):
    """Mixin to ensure user has 'user' role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'user'
    
    def handle_no_permission(self):
        messages.error(self.request, 'Sizda bu sahifaga kirish huquqi yo\'q!')
        return redirect('home')


class AdminRoleMixin(UserPassesTestMixin):
    """Mixin to ensure user has 'admin' role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'
    
    def handle_no_permission(self):
        messages.error(self.request, 'Sizda bu sahifaga kirish huquqi yo\'q!')
        return redirect('home')


class ModeratorRoleMixin(UserPassesTestMixin):
    """Mixin to ensure user has 'moderator' role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'moderator'
    
    def handle_no_permission(self):
        messages.error(self.request, 'Sizda bu sahifaga kirish huquqi yo\'q!')
        return redirect('home')


# ============================================================================
# USER VIEWS (ordinary citizen)
# ============================================================================

class UserDashboardView(LoginRequiredMixin, UserRoleMixin, TemplateView):
    """User dashboard with statistics"""
    template_name = 'complaints/user_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        user_complaints = Complaint.objects.filter(user=user)
        
        total_count = user_complaints.count()
        closed_count = user_complaints.filter(status='closed').count()
        in_progress_count = user_complaints.filter(status__in=['new', 'in_progress']).count()
        rejected_count = user_complaints.filter(status='rejected').count()

        success_rate = 0
        if total_count > 0:
            success_rate = round((closed_count / total_count) * 100, 1)

        recent_complaints = user_complaints.order_by('-created_at')[:5]

        context.update({
            'total_count': total_count,
            'closed_count': closed_count,
            'in_progress_count': in_progress_count,
            'rejected_count': rejected_count,
            'success_rate': success_rate,
            'recent_complaints': recent_complaints,
        })
        return context


class UserComplaintListView(LoginRequiredMixin, UserRoleMixin, ListView):
    """List of user's own complaints"""
    model = Complaint
    template_name = 'complaints/user_complaint_list.html'
    context_object_name = 'complaints'
    paginate_by = 10

    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user).order_by('-created_at')


class UserComplaintDetailView(LoginRequiredMixin, UserRoleMixin, DetailView):
    """Detail view of user's complaint"""
    model = Complaint
    template_name = 'complaints/user_complaint_detail.html'
    context_object_name = 'complaint'

    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user)


class UserComplaintCreateView(LoginRequiredMixin, UserRoleMixin, CreateView):
    """Create new complaint"""
    model = Complaint
    form_class = ComplaintCreateForm
    template_name = 'complaints/user_complaint_create.html'
    success_url = reverse_lazy('user_complaints')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Handle multiple image uploads
        images = self.request.FILES.getlist('images')
        for img in images:
            Image.objects.create(complaint=self.object, img=img)
        
        messages.success(self.request, 'Murojaatingiz muvaffaqiyatli yuborildi!')
        return response


class UserComplaintDeleteView(LoginRequiredMixin, UserRoleMixin, DeleteView):
    """Delete complaint (only if status is 'new')"""
    model = Complaint
    template_name = 'complaints/user_complaint_confirm_delete.html'
    success_url = reverse_lazy('user_complaints')

    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        complaint = self.get_object()

        if complaint.masul_tashkilot is not None:
            messages.error(request, "Tashkilot biriktirilgan murojaatni o'chira olmaysiz!")
            return redirect('user_complaint_detail', pk=complaint.pk)

        if complaint.status != 'new':
            messages.error(request, 'Faqat "Yangi" holatdagi murojaatlarni o\'chirishingiz mumkin!')
            return redirect('user_complaints')

        messages.success(request, 'Murojaat muvaffaqiyatli o\'chirildi!')
        return super().delete(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, UserRoleMixin, TemplateView):
    """User profile page"""
    template_name = 'complaints/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


# ============================================================================
# ADMIN VIEWS
# ============================================================================

class AdminDashboardView(LoginRequiredMixin, AdminRoleMixin, TemplateView):
    """Admin dashboard with full statistics"""
    template_name = 'complaints/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        all_complaints = Complaint.objects.all()
        
        # Status statistics
        total_count = all_complaints.count()
        new_count = all_complaints.filter(status='new').count()
        in_progress_count = all_complaints.filter(status='in_progress').count()
        closed_count = all_complaints.filter(status='closed').count()
        rejected_count = all_complaints.filter(status='rejected').count()
        
        # Priority statistics
        high_priority = all_complaints.filter(priority='high').count()
        medium_priority = all_complaints.filter(priority='medium').count()
        low_priority = all_complaints.filter(priority='low').count()
        
        # Region statistics
        region_stats = all_complaints.values('region__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Recent complaints
        recent_complaints = all_complaints.order_by('-created_at')[:10]
        
        context.update({
            'total_count': total_count,
            'new_count': new_count,
            'in_progress_count': in_progress_count,
            'closed_count': closed_count,
            'rejected_count': rejected_count,
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
            'region_stats': region_stats,
            'recent_complaints': recent_complaints,
        })
        return context


class AdminComplaintListView(LoginRequiredMixin, AdminRoleMixin, ListView):
    """Admin view of all complaints with filters"""
    model = Complaint
    template_name = 'complaints/admin_complaint_list.html'
    context_object_name = 'complaints'
    paginate_by = 20

    def get_queryset(self):
        queryset = Complaint.objects.all().order_by('-created_at')
        
        # Apply filters
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        region = self.request.GET.get('region')
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if region:
            queryset = queryset.filter(region_id=region)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['selected_region'] = self.request.GET.get('region', '')
        return context


class AdminComplaintDetailView(LoginRequiredMixin, AdminRoleMixin, DetailView):
    """Admin detail view of complaint"""
    model = Complaint
    template_name = 'complaints/admin_complaint_detail.html'
    context_object_name = 'complaint'


class AdminComplaintUpdateView(LoginRequiredMixin, AdminRoleMixin, UpdateView):
    """Admin update complaint (assign org, change priority, change status)"""
    model = Complaint
    form_class = ComplaintAdminUpdateForm
    template_name = 'complaints/admin_complaint_update.html'
    
    def get_success_url(self):
        return reverse_lazy('complaint_detail_admin', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if form.instance.status == 'closed' and not form.instance.answer_text:
            form.add_error('answer_text', 'Murojaatni yopish uchun javob matnini kiritishingiz kerak.')
            return self.form_invalid(form)

        if form.instance.status == 'closed' and not form.instance.closed_at:
            form.instance.closed_at = timezone.now()

        messages.success(self.request, 'Murojaat muvaffaqiyatli yangilandi!')
        return super().form_valid(form)


class AdminOrganizationListView(LoginRequiredMixin, AdminRoleMixin, ListView):
    """Admin view of all organizations"""
    model = Tashkilot
    template_name = 'complaints/admin_organization_list.html'
    context_object_name = 'organizations'
    paginate_by = 20


class AdminOrganizationCreateView(LoginRequiredMixin, AdminRoleMixin, CreateView):
    """Admin create organization"""
    model = Tashkilot
    form_class = TashkilotForm
    template_name = 'complaints/admin_organization_form.html'
    success_url = reverse_lazy('organizations_admin')

    def form_valid(self, form):
        messages.success(self.request, 'Tashkilot muvaffaqiyatli yaratildi!')
        return super().form_valid(form)


class AdminOrganizationUpdateView(LoginRequiredMixin, AdminRoleMixin, UpdateView):
    """Admin update organization"""
    model = Tashkilot
    form_class = TashkilotForm
    template_name = 'complaints/admin_organization_form.html'
    success_url = reverse_lazy('organizations_admin')

    def form_valid(self, form):
        messages.success(self.request, 'Tashkilot muvaffaqiyatli yangilandi!')
        return super().form_valid(form)


class AdminOrganizationDeleteView(LoginRequiredMixin, AdminRoleMixin, DeleteView):
    """Admin delete organization"""
    model = Tashkilot
    template_name = 'complaints/admin_organization_confirm_delete.html'
    success_url = reverse_lazy('organizations_admin')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tashkilot muvaffaqiyatli o\'chirildi!')
        return super().delete(request, *args, **kwargs)


class AdminPriorityManagementView(LoginRequiredMixin, AdminRoleMixin, ListView):
    """Admin priority management page - filter by priority and assign priority"""
    model = Complaint
    template_name = 'complaints/admin_priority_management.html'
    context_object_name = 'complaints'
    paginate_by = 20

    def get_queryset(self):
        queryset = Complaint.objects.all().order_by('-created_at')
        
        # Filter by priority
        priority_filter = self.request.GET.get('priority')
        if priority_filter == 'null':
            queryset = queryset.filter(priority__isnull=True)
        elif priority_filter in ['low', 'medium', 'high']:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_priority'] = self.request.GET.get('priority', '')
        
        # Count complaints by priority
        context['null_priority_count'] = Complaint.objects.filter(priority__isnull=True).count()
        context['low_priority_count'] = Complaint.objects.filter(priority='low').count()
        context['medium_priority_count'] = Complaint.objects.filter(priority='medium').count()
        context['high_priority_count'] = Complaint.objects.filter(priority='high').count()
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle priority assignment"""
        complaint_id = request.POST.get('complaint_id')
        new_priority = request.POST.get('priority')
        
        if complaint_id and new_priority in ['low', 'medium', 'high']:
            complaint = get_object_or_404(Complaint, id=complaint_id)
            complaint.priority = new_priority
            complaint.save()
            messages.success(request, f'Murojaat uchun "{dict(Complaint.PRIORITY_CHOICES)[new_priority]}" prioritet belgilandi!')
        
        return redirect(request.path + '?' + request.GET.urlencode())


class AdminUserListView(LoginRequiredMixin, AdminRoleMixin, ListView):
    """Admin list all users"""
    model = CustomUser
    template_name = 'complaints/admin_user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        return CustomUser.objects.all().order_by('-date_joined')


class AdminUserCreateView(LoginRequiredMixin, AdminRoleMixin, CreateView):
    """Admin create new user for organization"""
    model = CustomUser
    form_class = UserCreateForm
    template_name = 'complaints/admin_user_form.html'
    success_url = reverse_lazy('users_admin')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Assign user to organization and role
        organization = form.cleaned_data['organization']
        role = form.cleaned_data['role']
        
        # Set the organization and role on the user instance
        if organization:
            form.instance.tashkilot = organization
        form.instance.role = role
        form.instance.save()
        
        role_display = dict(CustomUser.ROLE_CHOICES).get(role, role)
        org_name = organization.name if organization else "tashkilotga biriktirilmagan"
        
        messages.success(self.request, f'Foydalanuvchi "{form.instance.username}" muvaffaqiyatli yaratildi! Rol: {role_display}, Tashkilot: {org_name}')
        return response


class AdminUserUpdateView(LoginRequiredMixin, AdminRoleMixin, UpdateView):
    """Admin update user"""
    model = CustomUser
    form_class = UserCreateForm
    template_name = 'complaints/admin_user_form.html'
    success_url = reverse_lazy('users_admin')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the current user instance to the form for password handling
        kwargs['instance'] = self.object
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        # Set initial values for organization and role
        initial['organization'] = self.object.tashkilot
        initial['role'] = self.object.role
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Assign user to organization and role
        organization = form.cleaned_data['organization']
        role = form.cleaned_data['role']
        
        # Set the organization and role on the user instance
        if organization:
            form.instance.tashkilot = organization
        else:
            form.instance.tashkilot = None
        form.instance.role = role
        form.instance.save()
        
        role_display = dict(CustomUser.ROLE_CHOICES).get(role, role)
        org_name = organization.name if organization else "tashkilotga biriktirilmagan"
        
        messages.success(self.request, f'Foydalanuvchi "{form.instance.username}" muvaffaqiyatli yangilandi! Rol: {role_display}, Tashkilot: {org_name}')
        return response


class AdminUserDeleteView(LoginRequiredMixin, AdminRoleMixin, DeleteView):
    """Admin delete user"""
    model = CustomUser
    template_name = 'complaints/admin_user_confirm_delete.html'
    success_url = reverse_lazy('users_admin')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, f'Foydalanuvchi muvaffaqiyatli o\'chirildi!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# MODERATOR VIEWS (organization staff)
# ============================================================================

class ModeratorDashboardView(LoginRequiredMixin, ModeratorRoleMixin, TemplateView):
    """Moderator dashboard showing assigned complaints"""
    template_name = 'complaints/moderator_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get complaints assigned to moderator's organization
        org_complaints = Complaint.objects.filter(masul_tashkilot=user.tashkilot)
        
        total_count = org_complaints.count()
        new_count = org_complaints.filter(status='new').count()
        in_progress_count = org_complaints.filter(status='in_progress').count()
        closed_count = org_complaints.filter(status='closed').count()
        
        recent_complaints = org_complaints.order_by('-created_at')[:10]
        
        context.update({
            'total_count': total_count,
            'new_count': new_count,
            'in_progress_count': in_progress_count,
            'closed_count': closed_count,
            'recent_complaints': recent_complaints,
            'organization': user.tashkilot,
        })
        return context


class ModeratorComplaintListView(LoginRequiredMixin, ModeratorRoleMixin, ListView):
    """Moderator view of assigned complaints"""
    model = Complaint
    template_name = 'complaints/moderator_complaint_list.html'
    context_object_name = 'complaints'
    paginate_by = 20

    def get_queryset(self):
        queryset = Complaint.objects.filter(
            masul_tashkilot=self.request.user.tashkilot
        ).order_by('-created_at')
        
        # Apply status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class ModeratorComplaintDetailView(LoginRequiredMixin, ModeratorRoleMixin, DetailView):
    """Moderator detail view of complaint"""
    model = Complaint
    template_name = 'complaints/moderator_complaint_detail.html'
    context_object_name = 'complaint'

    def get_queryset(self):
        return Complaint.objects.filter(masul_tashkilot=self.request.user.tashkilot)


class ModeratorComplaintUpdateView(LoginRequiredMixin, ModeratorRoleMixin, UpdateView):
    """Moderator update complaint (change status, add response)"""
    model = Complaint
    form_class = ComplaintModeratorUpdateForm
    template_name = 'complaints/moderator_complaint_update.html'
    
    def get_queryset(self):
        return Complaint.objects.filter(masul_tashkilot=self.request.user.tashkilot)
    
    def get_success_url(self):
        return reverse_lazy('complaint_detail_moderator', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if form.instance.status == 'closed' and not form.instance.answer_text:
            form.add_error('answer_text', 'Murojaatni yopish uchun javob matnini kiritishingiz kerak.')
            return self.form_invalid(form)

        if form.instance.status == 'closed' and not form.instance.closed_at:
            form.instance.closed_at = timezone.now()

        messages.success(self.request, 'Murojaat muvaffaqiyatli yangilandi!')
        return super().form_valid(form)
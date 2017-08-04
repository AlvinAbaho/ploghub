from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegisterForm, ProfileForm
from django.contrib.auth import views, authenticate, login, get_user_model
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core import exceptions
from django.views import generic
from .forms import PostModelForm
from .models import Post
import markdown
import bleach
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class IndexView(generic.ListView):
    model = Post
    paginate_by = 10
    template_name = 'ploghubapp/home_page.html'

    def get(self, request):
        if request.GET.get('sort_by') == "new":
            all_results = self.model.objects.filter(deleted=False).order_by('-created')
            sort_by = "New"
        else:
            sort_by = "Popular"
            all_results = self.model.objects.filter(deleted=False).order_by('-rank')

        paginator = Paginator(all_results, self.paginate_by)

        page = request.GET.get('page')
        try:
            post_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            post_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            post_list = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {'post_list' : post_list, 'sort_by' : sort_by})


class LogoutView(LoginRequiredMixin, View):

    def get(self, request):
        template_response = views.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect(reverse('ploghubapp:login'))

class RegisterView(View):
    form_class  = RegisterForm
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form' : form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['username']
            new_password = form.cleaned_data['password']
            new_email = form.cleaned_data['email']

            if get_user_model().objects.filter(username=new_username).exists():
                messages.error(request, "Username not available, choose a different one")
                return render(request, self.template_name, {'form' : form})
            if new_email != '' and get_user_model().objects.filter(email=new_email).exists():
                messages.error(request, "Email not available, choose a different one")
                return render(request, self.template_name, {'form' : form})
            
            #validate password
            try:
                validate_password(new_password)
            except exceptions.ValidationError as e:
                form.errors['password'] = list(e.messages)
                return render(request, self.template_name, {'form' : form})

            user = get_user_model().objects.create_user(username=new_username, password=new_password, email=new_email)
            user = authenticate(username=new_username, password=new_password)
            if user is not None:
                login(request, user)
                return redirect(reverse('ploghubapp:profile'))
        else:
            return render(request, self.template_name, {'form' : form})

class ProfileView(LoginRequiredMixin, View):
    login_url = '/user/login/'
    form_class = ProfileForm
    template_name = 'registration/profile.html'

    def get(self, request, *args, **kwargs):
        data = {'about' : request.user.userprofile.about}
        if request.user.email != '':
            data['email'] = request.user.email
        form = self.form_class(initial = data)
        return render(request, self.template_name, {'form' : form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, initial={'email' : request.user.email, 'about' : request.user.userprofile.about})
        if form.is_valid():
            if form.has_changed():
                user = request.user
                
                for field in form.changed_data:
                    if field == 'email':
                        if form.cleaned_data[field] != '' and User.objects.filter(email=form.cleaned_data[field]).exclude(id=user.id).exists():
                            messages.error(request, "Email address is already in use")
                            return redirect(reverse('ploghubapp:profile'))
                    setattr(user, field, form.cleaned_data[field])
                user.save()
                user.userprofile.about = form.cleaned_data['about']
                user.userprofile.save()
                messages.success(request, "Profile has been updated")
                return redirect(reverse('ploghubapp:profile'))
            else:
                messages.info(request, "Data has not been changed")
                return redirect(reverse('ploghubapp:profile'))
        else:
            messages.error(request, "Invalid form data")
            return redirect(reverse('ploghubapp:profile'))

class PublicUserProfileView(View):
    template_name = 'registration/public_user_profile.html'

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        return render(request, self.template_name, {'user' : user})

class WriteView(LoginRequiredMixin, View):
    form_class  = PostModelForm
    template_name = 'ploghubapp/write.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form' : form})

    def post(self, request):
        form = self.form_class(request.POST)
        
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            body_html = markdown.markdown(body)
            body_html = bleach.clean(body_html, tags=settings.ARTICLE_TAGS, strip=True)
            article = Post(title=title, body=body, user=request.user, body_html=body_html)

            article.save()
            messages.success(request, 'Article has been submitted.')
            return redirect(reverse('ploghubapp:home_page'))
        else:
            return render(request, self.template_name, {'form' : form})

class ViewPost(generic.DetailView):

    template_name = 'ploghubapp/view_post.html'

    def get(self, request, pk, username, slug):
        post = get_object_or_404(Post, pk=pk)
        if post.deleted:
            messages.error(request, 'The post you tried to access has been deleted.')
            return redirect(reverse('ploghubapp:home_page', args=[name]))
        return render(request, self.template_name, {'post' : post})
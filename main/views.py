from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View
from django.views.generic import TemplateView  
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse_lazy, reverse
from .utils.recaptcha import verify_recaptcha
from django.utils.timezone import make_aware
from datetime import datetime
from .forms import CustomUserCreationForm, ContactForm, SuggestionForm, HelpMessageForm
from .models import Anime, User, Episode, Comment, Conversation, Suggestion, Category
import json
import time

MONTHS_ES = {'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril', 'May': 'mayo', 'June': 'junio', 'July': 'julio', 'August': 'agosto', 'September': 'septiembre', 'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre',}

# Vista del mapa del sitio
class SiteMapView(TemplateView):  
    template_name = 'sitemap.html'  


# Vista de inicio de sesión
class Login(LoginView):
    model = User
    fields = '__all__'
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
          messages.success(self.request, "¡Has iniciado sesión exitosamente!")
          return super().form_valid(form)

    # Si el inicio de sesión es correcto, te redirige al index
    def get_success_url(self):
        return reverse_lazy('anime_list')


# Vista de registro 
class Signup(FormView):
    template_name = 'signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('anime_list')

    # Verifica el reCAPTCHA antes de guardar el formulario
    def form_valid(self, form):
        token = self.request.POST.get("g-recaptcha-response")
        if not token or not verify_recaptcha(token):
            messages.error(self.request, "Error de reCAPTCHA. Intenta de nuevo.")
            return self.form_invalid(form)

        user = form.save()
        if user is not None:
            login(self.request, user)

        messages.success(self.request, "¡Te has registrado exitosamente!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['RECAPTCHA_SITE_KEY'] = settings.RECAPTCHA_SITE_KEY
        return context
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('anime_list')
        return super(Signup, self).get(*args, **kwargs)
    

# Vista para actualizar el perfil del usuario
class Profile(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['icon']   
    template_name = 'profile.html'
    success_url = reverse_lazy('anime_list')

    def get_object(self, queryset=None):
        return self.request.user


# Vista para mostrar los animes en el index
class AnimeList(ListView):
    model = Anime
    template_name = 'index.html'
    context_object_name = 'animes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categorias = (
            Category.objects
            .filter(animes__isnull=False) 
            .distinct()
            .prefetch_related('animes')     
        )

        context['categories'] = categorias

        # Agregamos los animes por categoría en un dict serializable
        categorias_json = {}
        for i, categoria in enumerate(categorias, start=1):
            animes = []
            for anime in categoria.animes.all():
                animes.append({
                    'title': anime.title,
                    'image': anime.image_detail.url,
                    'url': reverse('anime_detail', args=[anime.title])
                })
            categorias_json[f'animes-{i}'] = animes

        # Convertimos a JSON para pasarlo como un único bloque al template
        context['categories_json'] = json.dumps(categorias_json, cls=DjangoJSONEncoder)

        return context


# Vista para hacer busquedas de los animes
class SearchBar(ListView):
    model = Anime
    context_object_name = 'animes'
    template_name = 'search.html'

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        return Anime.objects.filter(title__icontains=query) if query else Anime.objects.all()

    # Búsqueda
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_value'] = self.request.GET.get('search', '')
        return context

    # Búsqueda asíncrona
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = [
                {
                    "title": anime.title,
                    "total_episodes": anime.total_episodes,
                    "image": anime.image_card.url,
                    "description": anime.description,
                    "url": reverse('anime_detail', args=[anime.title])
                }
                for anime in context['animes']
            ]
            return JsonResponse(data, safe=False)
        else:
            return super().render_to_response(context, **response_kwargs)


# Vista de ayuda
class Help(View):
    def get(self, request):
        return render(request, 'help.html') 


# Vista para mostrar a detalle el anime seleccionado y sus episodios
class AnimeDetail(LoginRequiredMixin, DetailView):
    model = Anime
    context_object_name = 'anime'
    template_name = 'anime_detail.html'
    
    # Muestra los capítulos del anime seleccionado
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['episodes'] = Episode.objects.filter(anime=self.object).order_by('episode_number')
        return context


# Vista para mostrar y poder ver el capitulo seleccionado del anime y comentarios
class EpisodeDetail(LoginRequiredMixin, DetailView):
    model = Episode
    context_object_name = 'episode'
    template_name = 'episode_detail.html'
    
    def get_object(self):
        anime_title = self.kwargs['anime_title']
        episode_number = self.kwargs['episode_number']
        anime = get_object_or_404(Anime, title=anime_title)
        return get_object_or_404(Episode, anime=anime, episode_number=episode_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anime'] = self.object.anime
        context['comments'] = Comment.objects.filter(episode=self.object)
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        content = request.POST.get("content")
        
        if content:
            Comment.objects.create(
                episode=self.object,
                anime=self.object.anime,
                user=request.user,
                content=content
            )
        
        return redirect(self.request.path_info)

    # Maneja el envio de comentarios en el capitulo
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' and self.request.GET.get("comment") == "1":
            return self.comment_async()
        return super().render_to_response(context, **response_kwargs)

    def comment_async(self):
        episode = self.get_object()

        try:
            last_ts = float(self.request.GET.get("after", "0"))
            last_dt = make_aware(datetime.fromtimestamp(last_ts))
        except ValueError:
            last_dt = None

        start_time = time.time()
        timeout = 25  # segundos

        while time.time() - start_time < timeout:
            if last_dt:
                new_comments = Comment.objects.filter(episode=episode, created_at__gt=last_dt)
            else:
                new_comments = Comment.objects.filter(episode=episode).order_by('created_at')

            if new_comments.exists():
                # Solo devolvemos mensajes que realmente son más nuevos
                comments_filtered = []
                for comment in new_comments:
                    comment_ts = comment.created_at.timestamp()
                    if comment_ts > last_ts:
                        date = comment.created_at
                        month = MONTHS_ES[date.strftime('%B')]
                        format_date = f"{date.day} de {month} de {date.year} a las {date.strftime('%H:%M')}"

                        comments_filtered.append({
                            'user': comment.user.username,
                            'comment': comment.content,
                            'created_at': format_date,
                            'timestamp': comment_ts,
                        })

                if comments_filtered:
                    return JsonResponse(comments_filtered, safe=False)

            time.sleep(0.2)

        return JsonResponse([], safe=False)
    

# Vista de contacto
class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact') 

    # Maneja el envio del formulario de contacto
    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject'] or 'Contacto TakosuAnime'
        message = form.cleaned_data['message']
        body = (
            f"Nombre: {name}\n"
            f"Email de contacto: {email}\n\n"
            f"{message}"
        )

        correo = EmailMessage(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, to=[settings.DEFAULT_FROM_EMAIL], headers={'Reply-To': form.cleaned_data['email']})
        correo.send(fail_silently=False)
        messages.success(self.request, "¡Correo enviado, te responderemos lo mas pronto posible!")
        return super().form_valid(form)


# Vista de Buzón de sugerencias
class SuggestionView(LoginRequiredMixin, FormView):
    template_name = 'suggestion.html'
    form_class = SuggestionForm
    success_url = reverse_lazy('suggestion')  

    # Maneja el envio del formulario de sugerencias
    def form_valid(self, form):
        suggestion = form.save(commit=False)
        if self.request.user.is_authenticated:
            suggestion.user = self.request.user
        suggestion.save()
        messages.success(self.request, "¡Sugerencia enviada!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['suggestions'] = Suggestion.objects.select_related('user').order_by('-created_at')
        return context


# Vista del chat
class ConversationList(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'conversation_list.html'
    context_object_name = 'conversations'

    # Obtiene la conversacion del usuario o todas las conversaciones si es administrador
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Conversation.objects.all()
        else:
            return Conversation.objects.filter(user=user)
        

# Vista del chat de ayuda
class HelpChat(LoginRequiredMixin, FormView, DetailView):
    template_name = 'help_chat.html'
    model = Conversation
    form_class = HelpMessageForm
    context_object_name = 'conversation'

    # Obtiene el objeto de la conversación, asegurando que el usuario tenga permiso para acceder a ella
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_superuser and obj.user != self.request.user:
            raise PermissionDenied()
        return obj

    # Redirige a la conversación específica después de enviar un mensaje
    def get_success_url(self):
        return reverse_lazy('conversation_detail', kwargs={'pk': self.get_object().pk})
    
    # Maneja el envio del formulario de mensajes en la conversación
    def form_valid(self, form):
        msg = form.save(commit=False)
        msg.sender = self.request.user
        msg.conversation = self.get_object()
        if self.request.user.is_superuser:
            msg.recipient = self.get_object().user
        else:
            msg.recipient = None
        msg.save()
        return super().form_valid(form)
    
    # Muestra los mensajes de la conversación
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_messages'] = self.get_object().messages.order_by('created_at')
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' and self.request.GET.get("message") == "1":
            return self.chat_async()
        return super().render_to_response(context, **response_kwargs)

    # Maneja el chat de forma asíncrona
    def chat_async(self):
        conversation = self.get_object()

        try:
            last_ts = float(self.request.GET.get("after", "0"))
            last_dt = make_aware(datetime.fromtimestamp(last_ts))
        except ValueError:
            last_dt = None

        start_time = time.time()
        timeout = 25  # segundos

        while time.time() - start_time < timeout:
            if last_dt:
                new_messages = conversation.messages.filter(
                    created_at__gt=last_dt
                ).order_by('created_at').select_related('sender')
            else:
                new_messages = conversation.messages.all().order_by('created_at').select_related('sender')

            if new_messages.exists():
                # Solo devolvemos mensajes que realmente son más nuevos
                msgs_filtered = []
                for msg in new_messages:
                    msg_ts = msg.created_at.timestamp()
                    if msg_ts > last_ts:
                        date = msg.created_at
                        month = MONTHS_ES[date.strftime('%B')]
                        format_date = f"{date.day} de {month} de {date.year} a las {date.strftime('%H:%M')}"

                        msgs_filtered.append({
                            'sender': msg.sender.username,
                            'icon': msg.sender.icon.url if msg.sender.icon else '',
                            'message': msg.message,
                            'created_at': format_date,
                            'timestamp': msg_ts,
                            'is_user': msg.sender == self.request.user
                        })

                if msgs_filtered:
                    return JsonResponse(msgs_filtered, safe=False)

            time.sleep(0.5)

        return JsonResponse([], safe=False)

        

# Vista para redirigir al usuario a su conversación o a la lista de conversaciones si es administrador
class RedirectToConversation(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            return redirect('conversation_list')
        else:
            conversation, created = Conversation.objects.get_or_create(user=user)
            return redirect('conversation_detail', pk=conversation.pk)
        

# Manejo de errores personalizados
def custom_error_view(request, exception=None, status_code=500, message="Ha ocurrido un error"):
    context = {
        "status_code": status_code,
        "message": message
    }
    return render(request, "error.html", context=context, status=status_code)

def error_404_view(request, exception):
    return custom_error_view(request, exception, 404, "La página que buscas no fue encontrada.")

def error_500_view(request):
    return custom_error_view(request, status_code=500, message="Error interno del servidor.")

def error_403_view(request, exception):
    return custom_error_view(request, exception, 403, "Acceso denegado.")

def error_400_view(request, exception):
    return custom_error_view(request, exception, 400, "Solicitud incorrecta.")
import random
import re
from itertools import chain
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount


# Il faut être connecté pour accéder à la view index.html
@login_required(login_url='signin')
def index(request):
    # TODO: si un Profile n'a pas d'image (ex: kkun non connecté ou admin), erreur sur la view index.html
    # Je récupère l'objet User
    user_object = User.objects.get(username=request.user.username)
    # Je récupère l'objet Profile du User
    user_profile = Profile.objects.get(user=user_object)

    # Je crée une liste qui contiendra tous ceux que le user follow
    user_following_list = []
    feed = []

    # Je veux récupérer tous ceux que le user follow pour les rajouter à ma liste
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)

    # Je remplis la liste feed avec les objets Post d'un user que le user follow
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    # chain: It is a function that takes a series of iterables and returns one iterable (je compile les listes des posts des users que le user follow)
    feed_list = list(chain(*feed))

    # Je récupère tous les users
    all_users = User.objects.all()

    user_following_all = []

    # Pour chaque user que le user follow, je mets tous ces users dans une liste
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    # Je veux récupérer tous les users qui ne sont pas des users que le user follow
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    # Je récupère le current user pour l'enlever de la liste des suggestions (liste finale = tout le monde - ceux que je follow - moi)
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if x not in list(current_user)]

    # Je mélange le tout de manière aléatoire
    random.shuffle(final_suggestions_list)

    # J'initie deux listes
    username_profile = []
    username_profile_list = []

    # Dans une liste je mets les id des username identifiés dans ma liste finale
    for users in final_suggestions_list:
        username_profile.append(users.id)

    # Pour toutes les id que j'ai récupéré
    for ids in username_profile:
        # Je récupère les objets Profile liés aux id
        profile_lists = Profile.objects.filter(id_user=ids)
        # Tous les objets Profile sont mis dans une liste
        username_profile_list.append(profile_lists)

    # Je compile toutes les listes en une seule et je passe dans le render
    suggestions_username_profile_list = list(chain(*username_profile_list))

    # Je retourne la view index.html en ajoutant du context (je ne veux que les 4 premiers de ma liste de suggestions)
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})


@login_required(login_url='signin')
def settings(request):
    # Je récupère le Profile de l'utilisateur et je le passe à la view
    user_profile = Profile.objects.get(user=request.user)

    # Pour MAJ mon objet Profile
    if request.method == 'POST':
        # Si l'image n'est pas fournie
        if request.FILES.get('image') is None:
            # Je lui assigne l'image par défaut de la classe Profile
            image = user_profile.profile_img
        # Si l'image est fournie
        else:
            image = request.FILES.get('image')
        # Pour le reste des informations
        bio = request.POST['bio']
        location = request.POST['location']
        # J'écrase les valeurs déjà existantes
        user_profile.profile_img = image
        user_profile.bio = bio
        user_profile.location = location
        # Je sauvegarde
        user_profile.save()

        return redirect('settings')
    return render(request, 'setting.html', context={'user_profile': user_profile})


@login_required(login_url='signin')
def search(request):
    # Je récupère l'objet User et l'objet Profile du User pour le passer à la view dans le render
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        # Je récupère le username envoyé par le formulaire
        username = request.POST['username']
        # Je recherche les objets dans lesquels il y a le username de ma recherche
        username_object = User.objects.filter(username__icontains=username)

        # J'initie deux listes
        username_profile = []
        username_profile_list = []

        # Dans une liste je mets les id des username identifiés dans username_object
        for users in username_object:
            username_profile.append(users.id)

        # Pour toutes les id que j'ai récupéré
        for ids in username_profile:
            # Je récupère les objets Profile liés aux id
            profile_lists = Profile.objects.filter(id_user=ids)
            # Tous les objets Profile sont mis dans une liste
            username_profile_list.append(profile_lists)

        # Je compile toutes les listes en une seule et je passe dans le render
        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def profile(request, profile_pk):
    # Récupération du user
    user_object = User.objects.get(username=profile_pk)
    # Récupération du Profile du user
    user_profile = Profile.objects.get(user=user_object)
    # Je récupère les posts du user
    user_posts = Post.objects.filter(user=profile_pk)
    # Pour afficher le nombre de posts du user
    user_post_length = len(user_posts)

    # Je récupère le follower et le user
    follower = request.user.username
    user = profile_pk
    # Selon s'il existe un objet FollowersCount ou non je change le text_button et je l'envoie au context
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Ne plus suivre'
    else:
        button_text = 'Suivre'

    # Je veux récupérer le nombre de followers qui follow un user
    user_followers = len(FollowersCount.objects.filter(user=profile_pk))
    # Je veux récupérer le nombre de follow que possède un user
    user_following = len(FollowersCount.objects.filter(follower=profile_pk))

    # Définition du context que je ferai passer à la view pour accéder aux attributs des objets
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        # Je récupère les données du formulaire
        follower = request.POST['follower']
        user = request.POST['user']

        # Si l'user est déjà suivi, s'il y a déjà un objet FollowersCount
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            # Je le supprime
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            # Je redirige sur le profil du user
            return redirect('/profile/'+user)
        # Sinon je crée un nouvel objet FollowersCount
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            # Je redirige sur le profil du user
            return redirect('/profile/'+user)
    else:
        return redirect('/')


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        # Je récupère les données pour le nouveau Post
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        # Je crée un nouvel objet Post
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def like_post(request):
    # Je récupère le username du user connecté
    username = request.user.username
    # Je récupère l'id du post dans l'url
    post_id = request.GET.get('post_id')
    # Je récupère le Post avec son id, id récupérée dans l'url
    post = Post.objects.get(id=post_id)
    # Je regarde s'il existe déjà un LikePost avec l'id et le nom récupérés, cela retourne une liste et je ne veux que le 1er
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    # Si il n'y a pas déjà de LikePost avec cette id et nom
    if like_filter is None:
        # Je crée un nouvel objet LikePost
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        # J'incrémente le nombre de like du Post
        post.no_of_likes += 1
        post.save()
        return redirect('/')
    else:
        # Si 'objet existe déjà je le supprime (j'unlike le post)
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect('/')


def signup(request):
    # Si l'utilisateur est connecté, je ne veux pas qu'il accède à la view signup
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        # Je récupère les valeurs des inputs
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Controle username
        if username == '' or username is None:
            messages.error(request, "Veuillez indiquer un nom d'utilisateur.")
            return redirect('signup')
        if len(username) < 3:
            messages.error(request, "Le nom d'utilisateur doit comporter au minimum 3 caractères.")
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return redirect('signup')

        # Controle email
        if email == '' or email is None:
            messages.error(request, "Veuillez indiquer un email.")
            return redirect('signup')
        if not validate_email_address(email):
            messages.error(request, "L'e-mail n'est pas valide.")
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet e-mail est déjà pris.")
            return redirect('signup')

        # Controle password
        if password == '' or password is None:
            messages.error(request, "Veuillez indiquer un mot de passe.")
            return redirect('signup')
        if not validate_password(password):
            messages.error(request, "Le mot de passe doit contenir au minimum 8 caractères, au moins une majuscule, une minuscule, un chiffre et un caractère spécial.")
            return redirect('signup')
        if password != password2:
            messages.error(request, "Les mots de passe sont différents.")
            return redirect('signup')

        # Création de l'utilisateur
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Connection de l'utilisateur
        user_login = auth.authenticate(username=username, password=password)
        auth.login(request, user_login)

        # Création d'un objet Profile pour le nouvel utilisateur
        user_model = User.objects.get(username=username)
        new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
        new_profile.save()

        # Redirection sur l'accueil
        return redirect('/')

    return render(request, 'signup.html')


def signin(request):
    # Si l'utilisateur est connecté, je ne veux pas qu'il accède à la view signin
    if request.user.is_authenticated:
        return redirect('/')

    # Je test la validité du formulaire
    if request.method == 'POST':
        # Je récupère les informations des inputs
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        # Contrôle du username
        if username == "":
            messages.info(request, "Veuillez indiquer un nom d'utilisateur")
            return redirect('signin')
        # Contrôle du password
        elif password == "":
            messages.info(request, "Veuillez indiquer un mot de passe")
            return redirect('signin')
        else:
            # Si l'utilisateur existe en BDD, je le connecte et je redirige sur la view index
            if user is not None:
                auth.login(request, user)
                return redirect('/')
            # Sinon je lui indique un message d'erreur et je le redirige sur le formulaire
            else:
                messages.info(request, 'Informations de connexion incorrectes')
                return redirect('signin')

    return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    # Je déconnecte
    auth.logout(request)

    # Je retourne sur l'index
    return redirect('signin')


def validate_email_address(email_address):
    # Validation email REGEX
    return re.search(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email_address)


def validate_password(password):
    # Validation email REGEX
    return re.search(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}', password)

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Gestión personalizada de usuarios
class AccountManager(BaseUserManager):
    """Manager para crear usuarios y superusuarios."""
    
    def create_user(self, first_name, last_name, username, email, password=None):
        """Crea y retorna un usuario normal con email y username."""
        if not email:
            raise ValueError('El usuario debe tener un email')
        if not username:
            raise ValueError('El usuario debe tener un username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        """Crea y retorna un superusuario con permisos de administrador completo."""
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

# Modelo principal de usuario
class Account(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario personalizado con email como identificador."""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=50, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = AccountManager()

    def full_name(self):
        """Retorna el nombre completo del usuario."""
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Verifica permisos de usuario."""
        return self.is_admin

    def has_module_perms(self, app_label):
        """Verifica permisos sobre módulos."""
        return True

# Perfil adicional de usuario
class UserProfile(models.Model):
    """Información de perfil extendido para usuarios."""
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_1 = models.CharField(blank=True, max_length=100)
    address_2 = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile')
    city = models.CharField(blank=True, max_length=20)
    province = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        """Retorna la dirección completa concatenando address_1 y address_2."""
        return f'{self.address_1} {self.address_2}'


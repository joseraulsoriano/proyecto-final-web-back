import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';
import { User, UpdateProfileRequest } from '../../shared/interfaces/user.interface';
import { getApiBaseUrl } from '../../core/config/app.config';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './profile.html',
  styleUrl: './profile.scss'
})
export class ProfileComponent implements OnInit {
  profileForm!: FormGroup;
  user: User | null = null;
  loading = false;
  error: string | null = null;
  success: string | null = null;
  selectedFile: File | null = null;
  previewUrl: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getCurrentUserValue();
    
    if (!this.user) {
      this.authService.getCurrentUser().subscribe({
        next: (user) => {
          this.user = user;
          this.initForm();
          if (user.profile_picture) {
            this.previewUrl = this.getProfilePictureUrl(user.profile_picture);
          }
        },
        error: () => this.router.navigate(['/auth/login'])
      });
    } else {
      this.initForm();
      if (this.user.profile_picture) {
        this.previewUrl = this.getProfilePictureUrl(this.user.profile_picture);
      }
    }
  }

  getProfilePictureUrl(url: string | null | undefined): string | null {
    if (!url) return null;
    // Si la URL ya es absoluta (http/https), usarla directamente
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    // Si es una ruta relativa, construir la URL completa con el backend
    const apiUrl = getApiBaseUrl().replace('/api', '');
    return `${apiUrl}${url.startsWith('/') ? url : '/' + url}`;
  }

  initForm(): void {
    if (!this.user) return;

    this.profileForm = this.fb.group({
      first_name: [this.user.first_name, [Validators.required]],
      last_name: [this.user.last_name, [Validators.required]],
      email: [{ value: this.user.email, disabled: true }]
    });
    
    // Deshabilitar email después de crear el formulario (mejor práctica)
    this.profileForm.get('email')?.disable();
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile = input.files[0];
      
      // Crear preview
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.previewUrl = e.target.result;
      };
      reader.readAsDataURL(this.selectedFile);
    }
  }

  removePhoto(): void {
    this.selectedFile = null;
    if (this.user?.profile_picture) {
      this.previewUrl = this.getProfilePictureUrl(this.user.profile_picture);
    } else {
      this.previewUrl = null;
    }
  }

  onSubmit(): void {
    if (this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.error = null;
    this.success = null;

    const formData = new FormData();
    const formValue = this.profileForm.value;
    
    formData.append('first_name', formValue.first_name);
    formData.append('last_name', formValue.last_name);
    
    if (this.selectedFile) {
      formData.append('profile_picture', this.selectedFile);
    }

    this.authService.updateProfile(formData).subscribe({
      next: (user) => {
        this.loading = false;
        this.user = user;
        this.success = 'Perfil actualizado correctamente';
        this.selectedFile = null;
        
        // Actualizar preview con la nueva URL de la foto
        if (user.profile_picture) {
          this.previewUrl = this.getProfilePictureUrl(user.profile_picture);
        } else if (!this.selectedFile) {
          // Si no hay foto nueva y no hay foto en el usuario, mantener el preview actual
          this.previewUrl = null;
        }
        
        // Limpiar mensaje después de 3 segundos
        setTimeout(() => {
          this.success = null;
        }, 3000);
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || err.error?.message || 'Error al actualizar el perfil';
      }
    });
  }

  get f() {
    return this.profileForm?.controls || {};
  }

  getRoleLabel(): string {
    if (!this.user) return '';
    switch (this.user.role) {
      case 'ADMIN':
        return 'Administrador';
      case 'PROFESSOR':
        return 'Profesor';
      case 'STUDENT':
        return 'Estudiante';
      default:
        return '';
    }
  }
}

import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../../core/services/auth.service';
import { AuthUser } from '../../../core/models/user.model';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss'],
})
export class ProfileComponent implements OnInit {
  user: AuthUser | null = null;

  constructor(private auth: AuthService) {}

  ngOnInit(): void {
    this.user = this.auth.getUser();
  }
}

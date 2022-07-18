import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {AuthService} from 'src/app/services/auth.service';
import {ApiService} from '../../services/api.service'

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  form: FormGroup
  disabled = false
  minEmailLength: number = 6;
  maxEmailLength: number = 254;
  minPassLength: number = 6;
  maxPassLength: number = 30;

  constructor(
    private _api: ApiService,
    private _auth: AuthService,
    private router: Router,
    public fb: FormBuilder
  ) {
  }

  ngOnInit(): void {
    this.form = this.fb.group({
      email: ['',
        Validators.required,
        Validators.maxLength(this.maxEmailLength),
        Validators.minLength(this.minEmailLength),
        Validators.pattern('^([a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+)*$')],
      password: ['',
        Validators.required,
        Validators.minLength(this.minPassLength),
        Validators.maxLength(this.maxPassLength)],
      username: ['',]
    })
    ;
  }

  login() {
    this.disabled=true;
    if (!this.form.valid) {
      this.form.markAllAsTouched();
      this.disabled = false;
      return;
    }
    let b = this.form.value
    this._api.postTypeRequest('login', b).subscribe((res: any) => {
      console.log(res)
      if (res.access_token) {
        res.access_token = res.access_token.replace(/^"(.*)"$/, '$1'); // Remove quotes from token start/end. This is a temp fix?!
        this._auth.setDataInLocalStorage('token', res.access_token)
        this.router.navigate(['home'])
      }
    }, err => {
      this.disabled = false;
      console.log(err)
    });
  }

}

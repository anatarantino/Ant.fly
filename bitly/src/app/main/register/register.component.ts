import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {ApiService} from "../../services/api.service";
import {AuthService} from "../../services/auth.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  constructor(
    private _api: ApiService,
    private _auth: AuthService,
    private router: Router,
    public fb: FormBuilder
  ) {
  }

  form: FormGroup
  disabled = false
  minEmailLength: number = 6;
  maxEmailLength: number = 254;
  minPassLength: number = 6;
  maxPassLength: number = 30;
  minUserLength: number = 3;
  maxUserLength: number = 30;

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
      username: ['',
        Validators.required,
        Validators.minLength(this.minUserLength),
        Validators.maxLength(this.maxUserLength)]
    })
    ;
  }

  register() {
    if (!this.form.valid) {
      this.form.markAllAsTouched();
      return;
    }
    let b = this.form.value
    this._api.postTypeRequest('register', b).subscribe((res: any) => {
      if (res.status_code == 200) {
        this._api.postTypeRequest('login', b).subscribe((res: any) => {
          if (res.access_token) {
            this._auth.setDataInLocalStorage('token', res.access_token)
            this.router.navigate(['home'])
          }
        }, err => {
          console.log(err)
        })
      }
    }, err => {
      console.log(err)
    });
  }

}

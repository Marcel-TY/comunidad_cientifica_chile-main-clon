import { provideHttpClient, withXsrfConfiguration } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { App } from './app';

describe('Research catalog app', () => {
  let httpTesting: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideHttpClient(withXsrfConfiguration({
          cookieName: 'csrftoken',
          headerName: 'X-CSRFToken',
        })),
        provideHttpClientTesting(),
      ],
    }).compileComponents();
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  it('loads the catalog through the REST API', () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();

    httpTesting.expectOne('/api/research/').flush({
      projects: [],
      researchers: [],
      publications: [],
    });
    httpTesting.expectOne('/api/research/session/').flush({
      authenticated: false,
      isStaff: false,
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('h1')?.textContent).toContain(
      'Investigación científica',
    );
    expect(fixture.componentInstance.canManage).toBeFalse();
  });
});

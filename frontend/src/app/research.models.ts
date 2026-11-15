export interface ResearchProject {
  id: number;
  slug: string;
  title: string;
  summary: string;
  description: string;
  researchArea: string;
  funder: string;
  status: string;
  statusLabel: string;
  start_date: string | null;
  end_date: string | null;
  researcherIds: number[];
}

export interface Researcher {
  id: number;
  fullName: string;
  institution: string;
  expertise: string;
  biography: string;
  orcid: string;
}

export interface ScientificPublication {
  id: number;
  title: string;
  abstract: string;
  journal: string;
  doi: string;
  publicationDate: string;
  projectId: number | null;
  projectTitle: string | null;
  researcherIds: number[];
  researcherNames: string[];
}

export interface ResearchCatalogData {
  projects: ResearchProject[];
  researchers: Researcher[];
  publications: ScientificPublication[];
}

export interface ResearchSession {
  authenticated: boolean;
  isStaff: boolean;
}

export type ResearchProjectInput = Omit<
  ResearchProject,
  'id' | 'slug' | 'statusLabel'
> & { slug?: string };

export type ResearcherInput = Omit<Researcher, 'id'> & { email?: string };

export type ScientificPublicationInput = Omit<
  ScientificPublication,
  'id' | 'projectTitle' | 'researcherNames'
>;

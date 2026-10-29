export interface ResearchProject {
  id: number;
  title: string;
  summary: string;
  description: string;
  researchArea: string;
  funder: string;
  status: string;
  researcherIds: number[];
}

export interface Researcher {
  id: number;
  fullName: string;
  institution: string;
  expertise: string;
  biography: string;
}

export interface ScientificPublication {
  id: number;
  title: string;
  abstract: string;
  journal: string;
  doi: string;
  publicationDate: string;
  projectTitle: string;
  researcherNames: string[];
}

export interface ResearchCatalogData {
  projects: ResearchProject[];
  researchers: Researcher[];
  publications: ScientificPublication[];
}

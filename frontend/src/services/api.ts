import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class APIClient {
  private client: AxiosInstance;
  private isOnline: boolean = navigator.onLine;
  private offlineQueue: any[] = [];

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    window.addEventListener('online', () => this.syncOfflineData());
    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  private async makeRequest(method: string, url: string, data?: any) {
    try {
      const response = await this.client.request({
        method,
        url,
        data,
      });
      return response.data;
    } catch (error) {
      if (!navigator.onLine) {
        // Store for offline sync
        this.offlineQueue.push({ method, url, data, timestamp: Date.now() });
        return this.getFromLocalStorage(url) || { offline: true, message: 'Working offline' };
      }
      throw error;
    }
  }

  // Patient endpoints
  async getPatients() {
    return this.makeRequest('GET', '/patients');
  }

  async getPatient(id: number) {
    return this.makeRequest('GET', `/patients/${id}`);
  }

  async createPatient(data: any) {
    const response = await this.makeRequest('POST', '/patients', data);
    this.saveToLocalStorage(`/patients/${response.id}`, response);
    return response;
  }

  async updatePatient(id: number, data: any) {
    return this.makeRequest('PUT', `/patients/${id}`, data);
  }

  // Diagnosis endpoints
  async analyzeBloodTest(data: any) {
    const response = await this.makeRequest('POST', '/diagnosis/blood', data);
    this.saveToLocalStorage('/diagnosis/blood', response);
    return response;
  }

  async analyzeImage(data: any) {
    return this.makeRequest('POST', '/diagnosis/image', data);
  }

  async getPatientDiagnoses(patientId: number) {
    return this.makeRequest('GET', `/diagnosis/patient/${patientId}/diagnoses`);
  }

  // Drug endpoints
  async checkDrugInteraction(drug1: string, drug2: string) {
    return this.makeRequest('POST', '/drugs/check-interaction', { drug1, drug2 });
  }

  async checkPatientDrugs(patientId: number, drugs: string[]) {
    return this.makeRequest('POST', '/drugs/check-patient-drugs', {
      patient_id: patientId,
      drugs,
    });
  }

  async searchDrug(drugName: string) {
    return this.makeRequest('GET', `/drugs/search/${drugName}`);
  }

  // Local storage helpers
  private saveToLocalStorage(key: string, data: any) {
    const cache = JSON.parse(localStorage.getItem('api_cache') || '{}');
    cache[key] = {
      data,
      timestamp: Date.now(),
    };
    localStorage.setItem('api_cache', JSON.stringify(cache));
  }

  private getFromLocalStorage(key: string) {
    const cache = JSON.parse(localStorage.getItem('api_cache') || '{}');
    return cache[key]?.data;
  }

  private async syncOfflineData() {
    const queue = [...this.offlineQueue];
    this.offlineQueue = [];

    for (const request of queue) {
      try {
        await this.makeRequest(request.method, request.url, request.data);
      } catch (error) {
        console.error('Failed to sync:', error);
        this.offlineQueue.push(request);
      }
    }
  }
}

export const apiClient = new APIClient();
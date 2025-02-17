import { HttpClient } from "@angular/common/http";
import { Injectable, inject, signal } from "@angular/core";
import { Subject, Observable, switchMap, tap } from "rxjs";
import { environment } from "src/environments/environment";
import { PaperRelevanceResult } from "./types";

@Injectable({
    providedIn: "root",
})
export class AddDataStore {
    #http = inject(HttpClient);
    addDataSubject = new Subject<string>();
    searchResults = signal([] as PaperRelevanceResult[]);
    loading = signal(false);
    
    constructor() {
        this.addDataSubject
            .pipe(
                tap(() => this.loading.set(true)),
                switchMap((searchTerm) => this.searchPapers(searchTerm))
            )
            .subscribe((results) => {
                this.searchResults.set(results);
                this.loading.set(false);
            });
    }

    searchPapers(searchTerm: string): Observable<PaperRelevanceResult[]> {
        return this.#http.get<PaperRelevanceResult[]>(`${environment.apiBaseUrl}/papers/search/relevance?query=${searchTerm}`);
    }

    search(searchTerm: string) {
        this.addDataSubject.next(searchTerm);
    }

    addPapersToGraph(paperIds: string[]) {
        return this.#http.post(`${environment.apiBaseUrl}/papers/add`, paperIds);
    }

    clearResults() {
        this.searchResults.set([]);
    }
}

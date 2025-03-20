const splitSize=500
export const saveSearchResultsToSessionStorage = (results: any[]) => {
    for (let i = 0; i < results.length; i+=splitSize) {
      if (i+splitSize > results.length) {
        sessionStorage.setItem(`searchResults${i}`, JSON.stringify(results.slice(i, results.length)));
      } else {
      sessionStorage.setItem(`searchResults${i}`, JSON.stringify(results.slice(i, i+100)));
      }
    }
  }
  

export const getSearchResultsFromSessionStorage = () => {
    const results: any[] = [];
    let i=0;
    while (sessionStorage.getItem(`searchResults${i}`)) {
        results.push(...JSON.parse(sessionStorage.getItem(`searchResults${i}`)!));
        i+=splitSize;
    }
    return results;
}
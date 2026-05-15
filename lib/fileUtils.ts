import { get, set } from 'idb-keyval';

export const saveProject = async (project: unknown) => set('editkick-project', project);
export const loadProject = async <T>() => get<T>('editkick-project');
export const revokeUrl = (url?: string | null) => url && URL.revokeObjectURL(url);

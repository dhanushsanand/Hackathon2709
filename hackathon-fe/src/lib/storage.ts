export interface StoredFile {
	id: string;
	name: string;
	size: number;
	type: string;
	uploadedAt: string; // ISO
	progress: number;
	url?: string;
	subject?: string;
	serverResponse?: {
		pdf_id: string;
		filename: string;
		message: string;
		status: string;
	};
}

export interface StoredSubject {
	id: string;
	name: string;
	description?: string;
	progress?: number;
	uploads: number;
	notes?: number;
	quizzes?: number;
	bestScore?: number;
	latestScore?: number;
	averageScore?: number;
	color?: string;
}

const SUBJECTS_KEY = 'app:subjects';
const UPLOADS_KEY = 'app:uploads';

function readJson<T>(key: string): T | null {
	try {
		const raw = localStorage.getItem(key);
		if (!raw) return null;
		return JSON.parse(raw) as T;
	} catch (err) {
		console.error('storage: failed to read', key, err);
		return null;
	}
}

function writeJson(key: string, val: any) {
	try {
		localStorage.setItem(key, JSON.stringify(val));
	} catch (err) {
		console.error('storage: failed to write', key, err);
	}
}

export function getSubjects(): StoredSubject[] {
	const s = readJson<StoredSubject[]>(SUBJECTS_KEY);
	return s ?? [];
}

export function saveSubjects(subjects: StoredSubject[]) {
	writeJson(SUBJECTS_KEY, subjects);
	// notify other windows/components
	window.dispatchEvent(new CustomEvent('app:storage-updated'));
}

export function getUploads(): StoredFile[] {
	const u = readJson<StoredFile[]>(UPLOADS_KEY);
	return u ?? [];
}

export function saveUploads(uploads: StoredFile[]) {
	writeJson(UPLOADS_KEY, uploads);
	window.dispatchEvent(new CustomEvent('app:storage-updated'));
}

export function clearUploads() {
	writeJson(UPLOADS_KEY, []);
	window.dispatchEvent(new CustomEvent('app:storage-updated'));
}

export function getUploadsBySubject(subjectName: string): StoredFile[] {
	const all = getUploads();
	return all.filter(u => (u.subject ?? '').toLowerCase() === subjectName.toLowerCase());
}

export function addFile(file: StoredFile) {
	const uploads = getUploads();
	// ensure uploadedAt is string
	const toSave: StoredFile = { ...file, uploadedAt: typeof file.uploadedAt === 'string' ? file.uploadedAt : new Date(file.uploadedAt).toISOString() };
	uploads.push(toSave);
	saveUploads(uploads);

	// Update subjects
	const subjects = getSubjects();
	const subjectName = (file.subject ?? '').trim();
	if (!subjectName) {
		// nothing to do
		return;
	}

	const idx = subjects.findIndex(s => s.name.toLowerCase() === subjectName.toLowerCase());
	if (idx >= 0) {
		subjects[idx].uploads = (subjects[idx].uploads || 0) + 1;
	} else {
		// create a lightweight subject entry
		const colors = ["bg-red-500", "bg-yellow-500", "bg-indigo-500", "bg-pink-500", "bg-teal-500", "bg-blue-500", "bg-green-500", "bg-purple-500"];
		const color = colors[Math.floor(Math.random() * colors.length)];
		subjects.push({
			id: Date.now().toString() + Math.random().toString(36).slice(2),
			name: subjectName,
			description: '',
			progress: 0,
			uploads: 1,
			notes: 0,
			quizzes: 0,
			bestScore: 0,
			latestScore: 0,
			averageScore: 0,
			color
		});
	}
	saveSubjects(subjects);
}

export function addSubject(subject: StoredSubject) {
	const subjects = getSubjects();
	subjects.push(subject);
	saveSubjects(subjects);
}

export function deleteSubjectById(id: string) {
	const subjects = getSubjects().filter(s => s.id !== id);
	saveSubjects(subjects);
}

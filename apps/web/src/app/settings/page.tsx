'use client';
import { useEffect, useState } from 'react';
import MarkdownEditor from '@/components/MarkdownEditor';

export default function SettingsPage() {
  const [tree, setTree] = useState<Record<string, string[]>>({});
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');

  useEffect(() => {
    fetch('http://localhost:8000/api/files/tree').then(r => r.json()).then(setTree).catch(console.error);
  }, []);

  const openFile = async (path: string) => {
    setSelectedPath(path);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const file: any = await fetch(`http://localhost:8000/api/files/read?path=${encodeURIComponent(path)}`).then(r => r.json());
    setFileContent(file.raw);
    setSaveMsg('');
  };

  const saveFile = async () => {
    if (!selectedPath) return;
    setSaving(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result: any = await fetch('http://localhost:8000/api/files/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: selectedPath, content: fileContent }),
      }).then(r => r.json());
      setSaveMsg(result.lint_warnings?.length ? 'Saved with warnings' : 'Saved.');
    } catch (e: unknown) {
      setSaveMsg(`Error: ${e instanceof Error ? e.message : String(e)}`);
    }
    setSaving(false);
  };

  const EDITABLE_DIRS = ['context', 'core', 'skills', 'playbooks', 'rubrics', 'prompts'];

  return (
    <div className="p-6 flex gap-4 h-full">
      <div className="w-64 shrink-0 border rounded-lg overflow-auto">
        <div className="p-3 border-b"><h2 className="text-sm font-medium">Files</h2></div>
        <div className="p-2 space-y-4">
          {EDITABLE_DIRS.map(dir => (
            <div key={dir}>
              <p className="text-xs font-semibold text-gray-500 uppercase px-2 mb-1">{dir}/</p>
              {(tree[dir] || []).map(path => (
                <button
                  key={path}
                  onClick={() => openFile(path)}
                  className={`w-full text-left text-xs px-2 py-1 rounded hover:bg-gray-100 truncate block ${selectedPath === path ? 'bg-gray-100' : ''}`}
                >
                  {path.replace(`${dir}/`, '')}
                </button>
              ))}
            </div>
          ))}
        </div>
      </div>
      <div className="flex-1 flex flex-col gap-2">
        {selectedPath ? (
          <>
            <div className="flex items-center justify-between">
              <p className="text-sm font-mono text-gray-500">{selectedPath}</p>
              <div className="flex items-center gap-2">
                {saveMsg && <span className="text-xs text-gray-500">{saveMsg}</span>}
                <button onClick={saveFile} disabled={saving} className="px-3 py-1 bg-black text-white rounded text-sm disabled:opacity-50">
                  {saving ? 'Saving...' : 'Save'}
                </button>
              </div>
            </div>
            <MarkdownEditor value={fileContent} onChange={setFileContent} />
          </>
        ) : (
          <div className="border rounded-lg p-6">
            <p className="text-gray-500">Select a file from the tree to edit it.</p>
          </div>
        )}
      </div>
    </div>
  );
}

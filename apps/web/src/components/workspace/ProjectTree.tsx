'use client';
import { useEffect, useState } from 'react';

interface ProjectTreeProps {
  projects: Array<{
    id: number;
    name: string;
    folders?: Array<{
      id: number;
      name: string;
      deliverables?: Array<{
        id: number;
        title: string;
        content_type: string;
      }>;
    }>;
  }>;
  selectedDeliverableId?: number;
  onSelectDeliverable?: (id: number) => void;
}

export default function ProjectTree({ projects, selectedDeliverableId, onSelectDeliverable }: ProjectTreeProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [folders, setFolders] = useState<Record<number, any[]>>({});

  const toggleProject = (projectId: number) => {
    const key = `project-${projectId}`;
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
    if (!expanded[key]) {
      fetchFolders(projectId);
    }
  };

  const fetchFolders = async (projectId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/projects/${projectId}/folders`);
      if (res.ok) {
        const data = await res.json();
        setFolders(prev => ({ ...prev, [projectId]: data }));
        data.forEach((f: any) => fetchDeliverables(f.id));
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDeliverables = async (folderId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/folders/${folderId}/deliverables`);
      if (res.ok) {
        const data = await res.json();
        setFolders(prev => {
          const updated = { ...prev };
          Object.keys(updated).forEach(projectId => {
            updated[parseInt(projectId)] = updated[parseInt(projectId)].map((f: any) =>
              f.id === folderId ? { ...f, deliverables: data } : f
            );
          });
          return updated;
        });
      }
    } catch (e) {
      console.error(e);
    }
  };

  const toggleFolder = (projectId: number, folderId: number) => {
    const key = `folder-${projectId}-${folderId}`;
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="h-full overflow-auto text-sm">
      {projects.map(project => (
        <div key={project.id} className="space-y-0">
          <button
            onClick={() => toggleProject(project.id)}
            className="w-full text-left px-2 py-1.5 hover:bg-gray-100 flex items-center gap-1"
          >
            <span className="text-gray-400 select-none">
              {expanded[`project-${project.id}`] ? '▼' : '▶'}
            </span>
            <span className="font-medium text-gray-900">{project.name}</span>
          </button>

          {expanded[`project-${project.id}`] && folders[project.id] && (
            <div className="pl-4 space-y-0">
              {folders[project.id].map((folder: any) => (
                <div key={folder.id}>
                  <button
                    onClick={() => toggleFolder(project.id, folder.id)}
                    className="w-full text-left px-2 py-1.5 hover:bg-gray-100 flex items-center gap-1"
                  >
                    <span className="text-gray-400 select-none">
                      {expanded[`folder-${project.id}-${folder.id}`] ? '▼' : '▶'}
                    </span>
                    <span className="text-gray-700">{folder.name}</span>
                  </button>

                  {expanded[`folder-${project.id}-${folder.id}`] && folder.deliverables && (
                    <div className="pl-4 space-y-0">
                      {folder.deliverables.map((deliv: any) => (
                        <button
                          key={deliv.id}
                          onClick={() => onSelectDeliverable?.(deliv.id)}
                          className={`w-full text-left px-2 py-1.5 rounded flex items-center gap-2 ${
                            selectedDeliverableId === deliv.id
                              ? 'bg-blue-100 text-blue-900'
                              : 'hover:bg-gray-100 text-gray-700'
                          }`}
                        >
                          <span className="inline-block border rounded px-1 text-[10px] font-mono bg-gray-100">
                            {deliv.content_type}
                          </span>
                          <span>{deliv.title}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

import React, { useState, useEffect } from "react";
import {
  teamService,
  departmentService,
  userService,
  getApiError,
} from "../services/api";
import TopHeader from "../components/TopHeader";

function FormModal({ title, open, onClose, onSubmit, submitting, formError, children }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto soft-shadow">
        <div className="p-6 border-b border-outline-variant/20 flex items-center justify-between">
          <h3 className="font-headline-lg text-lg font-bold text-on-surface">{title}</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-surface-container transition-colors">
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <form onSubmit={onSubmit} className="p-6 space-y-4">
          {formError && (
            <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
              <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
              <span>{formError}</span>
            </div>
          )}
          {children}
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-2.5 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-medium hover:bg-surface-container transition-colors">
              Cancel
            </button>
            <button type="submit" disabled={submitting} className="flex-1 py-2.5 rounded-xl bg-primary text-on-primary text-sm font-bold hover:opacity-90 transition-all disabled:opacity-50">
              {submitting ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function inputCls() {
  return "w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20";
}

function labelCls() {
  return "block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5";
}

function MembersModal({ open, title, onClose, members, users, onSubmit, onRemove, memberRoleLabel }) {
  const [user, setUser] = useState("");
  const [role, setRole] = useState("member");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (open) {
      setUser("");
      setRole("member");
      setError(null);
    }
  }, [open]);

  if (!open) return null;

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!user) return;
    setAdding(true);
    setError(null);
    try {
      await onSubmit({ user: Number(user), role });
      setUser("");
      setRole("member");
    } catch (err) {
      setError(getApiError(err, "Failed to add member."));
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[110] p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto soft-shadow">
        <div className="p-6 border-b border-outline-variant/20 flex items-center justify-between">
          <h3 className="font-headline-lg text-lg font-bold text-on-surface">{title}</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-surface-container transition-colors">
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <div className="p-6 space-y-4">
          <form onSubmit={handleAdd} className="flex gap-2 items-end">
            <div className="flex-1">
              <label className={labelCls()}>Add Member</label>
              <select value={user} onChange={(e) => setUser(e.target.value)} className={inputCls()}>
                <option value="">Select user</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {[u.first_name, u.last_name].filter(Boolean).join(" ") || u.username} ({u.email})
                  </option>
                ))}
              </select>
            </div>
            {memberRoleLabel && (
              <div>
                <label className={labelCls()}>Role</label>
                <select value={role} onChange={(e) => setRole(e.target.value)} className={inputCls()}>
                  {memberRoleLabel.map((r) => (
                    <option key={r.value} value={r.value}>{r.label}</option>
                  ))}
                </select>
              </div>
            )}
            <button
              type="submit"
              disabled={adding || !user}
              className="px-4 py-2.5 rounded-xl bg-primary text-on-primary text-sm font-bold hover:opacity-90 disabled:opacity-50 whitespace-nowrap"
            >
              Add
            </button>
          </form>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <div className="divide-y divide-outline-variant/10">
            {members.length === 0 ? (
              <p className="text-sm text-on-surface-variant py-4 text-center">No members yet.</p>
            ) : (
              members.map((m) => (
                <div key={m.id} className="flex items-center gap-3 py-3">
                  <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-[18px] text-primary">person</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-on-surface truncate">{m.user_name || m.user_email}</p>
                    <p className="text-[11px] text-outline">
                      {m.user_email}
                      {m.is_head ? " · Head" : ""}
                      {m.role ? ` · ${m.role}` : ""}
                    </p>
                  </div>
                  <button onClick={() => onRemove(m)} className="p-1.5 rounded-lg hover:bg-red-50 transition-colors" title="Remove">
                    <span className="material-symbols-outlined text-[18px] text-red-500">person_remove</span>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TeamsDepartmentsPage() {
  const [tab, setTab] = useState("departments");
  const [departments, setDepartments] = useState([]);
  const [teams, setTeams] = useState([]);
  const [departmentMembers, setDepartmentMembers] = useState([]);
  const [teamMembers, setTeamMembers] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const [deptForm, setDeptForm] = useState(null);
  const [deptError, setDeptError] = useState(null);
  const [deptSaving, setDeptSaving] = useState(false);

  const [teamForm, setTeamForm] = useState(null);
  const [teamError, setTeamError] = useState(null);
  const [teamSaving, setTeamSaving] = useState(false);

  const [deptMembersFor, setDeptMembersFor] = useState(null);
  const [teamMembersFor, setTeamMembersFor] = useState(null);

  const fetchAll = async () => {
    setLoading(true);
    const [dRes, tRes, dmRes, tmRes, uRes] = await Promise.allSettled([
      departmentService.list(),
      teamService.list(),
      departmentService.members(),
      teamService.members(),
      userService.list({ page_size: 100 }),
    ]);
    if (dRes.status === "fulfilled") setDepartments(dRes.value.data.results || dRes.value.data || []);
    if (tRes.status === "fulfilled") setTeams(tRes.value.data.results || tRes.value.data || []);
    if (dmRes.status === "fulfilled") setDepartmentMembers(dmRes.value.data.results || dmRes.value.data || []);
    if (tmRes.status === "fulfilled") setTeamMembers(tmRes.value.data.results || tmRes.value.data || []);
    if (uRes.status === "fulfilled") setUsers(uRes.value.data.results || uRes.value.data || []);
    setLoading(false);
  };

  useEffect(() => {
    fetchAll();
  }, []);

  // ── Departments ─────────────────────────────────────────────
  const openDeptForm = (dept) => {
    setDeptForm(dept
      ? { id: dept.id, name: dept.name, code: dept.code, description: dept.description || "", head: dept.head || "", email: dept.email || "", phone: dept.phone || "", location: dept.location || "", status: dept.status || "active" }
      : { id: null, name: "", code: "", description: "", head: "", email: "", phone: "", location: "", status: "active" });
    setDeptError(null);
  };

  const saveDept = async (e) => {
    e.preventDefault();
    setDeptSaving(true);
    setDeptError(null);
    try {
      if (deptForm.id) await departmentService.update(deptForm.id, deptForm);
      else await departmentService.create(deptForm);
      setDeptForm(null);
      fetchAll();
    } catch (err) {
      setDeptError(getApiError(err, "Failed to save department."));
    } finally {
      setDeptSaving(false);
    }
  };

  const deleteDept = async (dept) => {
    if (!window.confirm(`Delete department "${dept.name}"?`)) return;
    try {
      await departmentService.delete(dept.id);
      fetchAll();
    } catch (err) {
      alert(getApiError(err, "Failed to delete department."));
    }
  };

  // ── Teams ───────────────────────────────────────────────────
  const openTeamForm = (team) => {
    setTeamForm(team
      ? { id: team.id, department: team.department, team_name: team.team_name, description: team.description || "", is_active: team.is_active }
      : { id: null, department: "", team_name: "", description: "", is_active: true });
    setTeamError(null);
  };

  const saveTeam = async (e) => {
    e.preventDefault();
    setTeamSaving(true);
    setTeamError(null);
    try {
      if (teamForm.id) await teamService.update(teamForm.id, teamForm);
      else await teamService.create(teamForm);
      setTeamForm(null);
      fetchAll();
    } catch (err) {
      setTeamError(getApiError(err, "Failed to save team."));
    } finally {
      setTeamSaving(false);
    }
  };

  const deleteTeam = async (team) => {
    if (!window.confirm(`Delete team "${team.team_name}"?`)) return;
    try {
      await teamService.delete(team.id);
      fetchAll();
    } catch (err) {
      alert(getApiError(err, "Failed to delete team."));
    }
  };

  const deptMembersById = (deptId) => departmentMembers.filter((m) => m.department === deptId);
  const teamMembersById = (teamId) => teamMembers.filter((m) => m.team === teamId);

  return (
    <div className="space-y-6">
      <TopHeader
        title="Teams & Departments"
        subtitle="Organize users into departments and teams"
        actions={
          tab === "departments" ? (
            <button
              onClick={() => openDeptForm(null)}
              className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              New Department
            </button>
          ) : (
            <button
              onClick={() => openTeamForm(null)}
              className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              New Team
            </button>
          )
        }
      />

      <div className="flex gap-2 border-b border-outline-variant/20">
        {["departments", "teams"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors ${tab === t ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"}`}
          >
            {t === "departments" ? "Departments" : "Teams"}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : tab === "departments" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {departments.length === 0 && (
            <div className="col-span-full bg-white rounded-xl soft-shadow border border-outline-variant/20 p-16 text-center">
              <span className="material-symbols-outlined text-[48px] text-outline-variant">account_tree</span>
              <p className="text-on-surface-variant mt-3 text-sm">No departments yet</p>
            </div>
          )}
          {departments.map((dept) => (
            <div key={dept.id} className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="material-symbols-outlined text-primary">account_tree</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-on-surface text-sm">{dept.name}</h3>
                    <p className="text-xs text-on-surface-variant">{dept.code}</p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => setDeptMembersFor(dept)} className="p-1.5 rounded-lg hover:bg-surface-container transition-colors" title="Members">
                    <span className="material-symbols-outlined text-[18px] text-outline-variant">group</span>
                  </button>
                  <button onClick={() => openDeptForm(dept)} className="p-1.5 rounded-lg hover:bg-surface-container transition-colors" title="Edit">
                    <span className="material-symbols-outlined text-[18px] text-outline-variant">edit</span>
                  </button>
                  <button onClick={() => deleteDept(dept)} className="p-1.5 rounded-lg hover:bg-red-50 transition-colors" title="Delete">
                    <span className="material-symbols-outlined text-[18px] text-red-500">delete</span>
                  </button>
                </div>
              </div>
              {dept.description && <p className="text-xs text-on-surface-variant line-clamp-2">{dept.description}</p>}
              <div className="mt-3 pt-3 border-t border-outline-variant/20 flex items-center justify-between text-xs text-on-surface-variant">
                <span>Head: {dept.head_name || "-"}</span>
                <span>{deptMembersById(dept.id).length} members</span>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${dept.status === "active" ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-600"}`}>
                  {dept.status}
                </span>
                <button onClick={() => setDeptMembersFor(dept)} className="text-primary text-xs font-semibold hover:underline">
                  Manage members
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {teams.length === 0 && (
            <div className="col-span-full bg-white rounded-xl soft-shadow border border-outline-variant/20 p-16 text-center">
              <span className="material-symbols-outlined text-[48px] text-outline-variant">groups</span>
              <p className="text-on-surface-variant mt-3 text-sm">No teams yet</p>
            </div>
          )}
          {teams.map((team) => (
            <div key={team.id} className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="material-symbols-outlined text-primary">groups</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-on-surface text-sm">{team.team_name}</h3>
                    <p className="text-xs text-on-surface-variant">{team.department_name || "No department"}</p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => setTeamMembersFor(team)} className="p-1.5 rounded-lg hover:bg-surface-container transition-colors" title="Members">
                    <span className="material-symbols-outlined text-[18px] text-outline-variant">group</span>
                  </button>
                  <button onClick={() => openTeamForm(team)} className="p-1.5 rounded-lg hover:bg-surface-container transition-colors" title="Edit">
                    <span className="material-symbols-outlined text-[18px] text-outline-variant">edit</span>
                  </button>
                  <button onClick={() => deleteTeam(team)} className="p-1.5 rounded-lg hover:bg-red-50 transition-colors" title="Delete">
                    <span className="material-symbols-outlined text-[18px] text-red-500">delete</span>
                  </button>
                </div>
              </div>
              {team.description && <p className="text-xs text-on-surface-variant line-clamp-2">{team.description}</p>}
              <div className="mt-3 pt-3 border-t border-outline-variant/20 flex items-center justify-between text-xs text-on-surface-variant">
                <span>{team.member_count ?? teamMembersById(team.id).length} members</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${team.is_active ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-600"}`}>
                  {team.is_active ? "Active" : "Inactive"}
                </span>
              </div>
              <div className="mt-2">
                <button onClick={() => setTeamMembersFor(team)} className="text-primary text-xs font-semibold hover:underline">
                  Manage members
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Department form modal */}
      <FormModal
        title={deptForm?.id ? "Edit Department" : "New Department"}
        open={!!deptForm}
        onClose={() => setDeptForm(null)}
        onSubmit={saveDept}
        submitting={deptSaving}
        formError={deptError}
      >
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls()}>Name *</label>
            <input type="text" required value={deptForm?.name || ""} onChange={(e) => setDeptForm({ ...deptForm, name: e.target.value })} className={inputCls()} />
          </div>
          <div>
            <label className={labelCls()}>Code *</label>
            <input type="text" required value={deptForm?.code || ""} onChange={(e) => setDeptForm({ ...deptForm, code: e.target.value })} placeholder="e.g. ENG" className={inputCls()} />
          </div>
        </div>
        <div>
          <label className={labelCls()}>Description</label>
          <textarea rows={2} value={deptForm?.description || ""} onChange={(e) => setDeptForm({ ...deptForm, description: e.target.value })} className={inputCls()} />
        </div>
        <div>
          <label className={labelCls()}>Department Head</label>
          <select value={deptForm?.head || ""} onChange={(e) => setDeptForm({ ...deptForm, head: e.target.value })} className={inputCls()}>
            <option value="">None</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {[u.first_name, u.last_name].filter(Boolean).join(" ") || u.username} ({u.email})
              </option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls()}>Email</label>
            <input type="email" value={deptForm?.email || ""} onChange={(e) => setDeptForm({ ...deptForm, email: e.target.value })} className={inputCls()} />
          </div>
          <div>
            <label className={labelCls()}>Phone</label>
            <input type="text" value={deptForm?.phone || ""} onChange={(e) => setDeptForm({ ...deptForm, phone: e.target.value })} className={inputCls()} />
          </div>
        </div>
        <div>
          <label className={labelCls()}>Location</label>
          <input type="text" value={deptForm?.location || ""} onChange={(e) => setDeptForm({ ...deptForm, location: e.target.value })} className={inputCls()} />
        </div>
        <div>
          <label className={labelCls()}>Status</label>
          <select value={deptForm?.status || "active"} onChange={(e) => setDeptForm({ ...deptForm, status: e.target.value })} className={inputCls()}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </FormModal>

      {/* Team form modal */}
      <FormModal
        title={teamForm?.id ? "Edit Team" : "New Team"}
        open={!!teamForm}
        onClose={() => setTeamForm(null)}
        onSubmit={saveTeam}
        submitting={teamSaving}
        formError={teamError}
      >
        <div>
          <label className={labelCls()}>Department *</label>
          <select required value={teamForm?.department || ""} onChange={(e) => setTeamForm({ ...teamForm, department: e.target.value })} className={inputCls()}>
            <option value="">Select department</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelCls()}>Team Name *</label>
          <input type="text" required value={teamForm?.team_name || ""} onChange={(e) => setTeamForm({ ...teamForm, team_name: e.target.value })} className={inputCls()} />
        </div>
        <div>
          <label className={labelCls()}>Description</label>
          <textarea rows={2} value={teamForm?.description || ""} onChange={(e) => setTeamForm({ ...teamForm, description: e.target.value })} className={inputCls()} />
        </div>
        <label className="flex items-center gap-2 text-sm text-on-surface">
          <input type="checkbox" checked={!!teamForm?.is_active} onChange={(e) => setTeamForm({ ...teamForm, is_active: e.target.checked })} />
          Active team
        </label>
      </FormModal>

      {/* Members modals */}
      <MembersModal
        open={!!deptMembersFor}
        title={`${deptMembersFor?.name || "Department"} Members`}
        onClose={() => setDeptMembersFor(null)}
        members={deptMembersFor ? deptMembersById(deptMembersFor.id) : []}
        users={users}
        memberRoleLabel={null}
        onSubmit={async (data) => {
          await departmentService.addMember({ user: data.user, department: deptMembersFor.id });
          fetchAll();
        }}
        onRemove={async (m) => {
          if (!window.confirm(`Remove ${m.user_email} from this department?`)) return;
          await departmentService.deleteMember(m.id);
          fetchAll();
        }}
      />
      <MembersModal
        open={!!teamMembersFor}
        title={`${teamMembersFor?.team_name || "Team"} Members`}
        onClose={() => setTeamMembersFor(null)}
        members={teamMembersFor ? teamMembersById(teamMembersFor.id) : []}
        users={users}
        memberRoleLabel={[
          { value: "member", label: "Member" },
          { value: "lead", label: "Lead" },
          { value: "manager", label: "Manager" },
        ]}
        onSubmit={async (data) => {
          await teamService.addMember({ user: data.user, role: data.role, team: teamMembersFor.id });
          fetchAll();
        }}
        onRemove={async (m) => {
          if (!window.confirm(`Remove ${m.user_email} from this team?`)) return;
          await teamService.deleteMember(m.id);
          fetchAll();
        }}
      />
    </div>
  );
}

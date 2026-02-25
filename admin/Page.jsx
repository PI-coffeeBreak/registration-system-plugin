import { useState, useEffect } from "react";
import { useApi, baseUrl, registerPluginTranslations } from "coffeebreak";
import { useActivities, useNotification, useMedia } from "coffeebreak/contexts";
import { useTranslation } from "react-i18next";
import { FaSearch, FaEdit, FaExclamationTriangle, FaTrash } from "react-icons/fa";
import en from "../locales/en.json";
import ptBR from "../locales/pt-BR.json";
import ptPT from "../locales/pt-PT.json";

const NS = "registration-system-plugin";
registerPluginTranslations(NS, { en, "pt-BR": ptBR, "pt-PT": ptPT });

const apiBase = `${baseUrl}/registration-system-plugin/activity-registration`;

// --- Shared UI ---

function DeleteModal({ isOpen, onClose, onConfirm, isLoading, title, message }) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-base-100 rounded-xl shadow-xl max-w-md w-full p-6">
        <h3 className="font-bold text-lg mb-4">{title}</h3>
        <div className="flex items-center gap-3 mb-4">
          <div className="text-primary"><FaExclamationTriangle size={24} /></div>
          <p>{message}</p>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button className="btn btn-ghost" onClick={onClose} disabled={isLoading}>Cancel</button>
          <button className="btn btn-primary" onClick={onConfirm} disabled={isLoading}>
            {isLoading ? <span className="loading loading-spinner loading-sm" /> : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}

// --- ActivityCard: displays a single activity with edit button ---

function ActivityCard({ activity, onEdit }) {
  const { t } = useTranslation(NS);
  const { getMediaUrl } = useMedia();
  const meta = activity.metadata;

  const imageUrl = activity.image
    ? (activity.image.startsWith("http") ? activity.image : getMediaUrl(activity.image))
    : null;

  return (
    <div className="group card bg-base-100 shadow-sm hover:shadow-lg transition-all duration-300 border-2 border-secondary hover:border-primary overflow-hidden h-[380px]">
      <div className="absolute top-2 right-2 z-10">
        <button
          className="p-2 bg-base-100/90 hover:bg-white text-base-content/60 hover:text-primary rounded-lg shadow-sm border border-transparent hover:border-primary/20"
          onClick={() => onEdit(activity.id)}
          aria-label={t("activities.edit")}
          type="button"
        >
          <FaEdit className="w-4 h-4" />
        </button>
      </div>

      <div className="h-40 w-full overflow-hidden bg-base-200 relative shrink-0">
        {imageUrl ? (
          <img src={imageUrl} alt={t("activities.imageAlt")} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full bg-base-200/50 flex items-center justify-center">
            <span className="text-base-content/40 text-sm italic">{t("activities.noImage")}</span>
          </div>
        )}
        {activity.type && (
          <div className="absolute bottom-3 left-3">
            <span className="badge border-none shadow-sm font-semibold px-3 py-3" style={{ backgroundColor: activity.type?.color || "var(--color-primary)", color: "#fff" }}>
              {activity.type?.type || activity.type}
            </span>
          </div>
        )}
      </div>

      <div className="card-body p-5 gap-1 shrink-0 h-[220px]">
        <h2 className="card-title text-lg font-bold text-primary line-clamp-1">{activity.name}</h2>
        {activity.topic && (
          <span className="badge badge-outline badge-sm text-xs opacity-70">{activity.topic}</span>
        )}
        <p className="text-sm text-base-content/80 line-clamp-3 leading-relaxed min-h-[4.5em]">
          {activity.description || <span className="italic opacity-50">{t("activities.noDescription")}</span>}
        </p>
        <div className="mt-auto pt-3 flex items-center border-t border-base-200">
          {meta?.is_restricted ? (
            <span className={`flex items-center gap-1.5 text-xs font-semibold ${meta.registered >= meta.slots ? "text-error" : "text-success"}`}>
              <span className={`w-2 h-2 rounded-full ${meta.registered >= meta.slots ? "bg-error" : "bg-success"}`} />
              {meta.registered} / {meta.slots} {t("activities.slots.label", "Slots")}
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-xs text-base-content/50">
              <span className="w-2 h-2 rounded-full bg-base-300" />
              {t("activities.slots.open", "Open Access")}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

// --- EditMetadataModal: self-contained, uses useApi + useNotification ---

function EditMetadataModal({ activityId, activityName, onUpdate, onClose }) {
  const api = useApi();
  const { showNotification } = useNotification();
  const { t } = useTranslation(NS);

  const [isRestricted, setIsRestricted] = useState(false);
  const [slots, setSlots] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (activityId) fetchMetadata();
  }, [activityId]);

  const fetchMetadata = async () => {
    setIsLoading(true);
    try {
      const { data } = await api.get(`${apiBase}/metadata/${activityId}`);
      setIsRestricted(data.is_restricted);
      setSlots(data.slots ?? "");
      setErrorMsg("");
    } catch {
      setIsRestricted(false);
      setSlots("");
      setErrorMsg(t("activities.slots.noMetadataInfo"));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    const parsedSlots = Number.parseInt(slots, 10);
    const params = { is_restricted: isRestricted };
    if (isRestricted) params.slots = Number.isNaN(parsedSlots) ? undefined : parsedSlots;

    try {
      await api.post(`${apiBase}/metadata/${activityId}`, null, { params });
      showNotification(t("activities.slots.saveSuccess"), "success");
      await onUpdate(activityId);
      onClose();
    } catch (err) {
      console.error(err);
      showNotification(t("activities.slots.saveError"), "error");
    }
  };

  if (!activityId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-base-100 rounded-xl shadow-xl max-w-xl w-full p-6">
        <button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2" type="button" onClick={onClose}>✕</button>
        <h3 className="font-bold text-lg mb-1">{t("activities.slots.modalTitle")}</h3>
        {activityName && <p className="text-sm font-bold text-secondary mb-4">{activityName}</p>}
        {errorMsg && (
          <div className="alert alert-info mb-4">
            <FaExclamationTriangle className="h-5 w-5" />
            <span>{errorMsg}</span>
          </div>
        )}
        <form onSubmit={handleSave}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center mb-6">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={isRestricted}
                onChange={(e) => { setIsRestricted(e.target.checked); setErrorMsg(""); }}
                className="checkbox checkbox-primary"
              />
              <span className="label-text">{t("activities.slots.limitLabel")}</span>
            </label>
            <input
              type="number"
              className="input input-bordered w-full"
              value={isRestricted ? slots : ""}
              onChange={(e) => setSlots(e.target.value)}
              placeholder={t("activities.slots.slotPlaceholder")}
              disabled={!isRestricted}
              min={0}
            />
          </div>
          <div className="modal-action">
            <button type="submit" className="btn btn-primary" disabled={isLoading}>
              {isLoading ? <span className="loading loading-spinner" /> : t("common.actions.save")}
            </button>
            <button type="button" className="btn" onClick={onClose}>{t("common.actions.cancel")}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

// --- Main page ---

export default function ActivitySlotsPage() {
  const api = useApi();
  const { activities, fetchActivities, getActivityType } = useActivities();
  const { t } = useTranslation(NS);

  const [activityData, setActivityData] = useState({});
  const [selectedActivityId, setSelectedActivityId] = useState(null);
  const [isLoadingData, setIsLoadingData] = useState(true);

  useEffect(() => {
    const load = async () => {
      setIsLoadingData(true);
      await fetchActivities();
      setIsLoadingData(false);
    };
    load();
  }, []);

  useEffect(() => {
    if (activities.length > 0) {
      fetchAllMetadata(activities.map((a) => a.id));
    }
  }, [activities]);

  const fetchAllMetadata = async (ids) => {
    const result = {};
    await Promise.all(
      ids.map(async (id) => {
        try {
          const [metadataRes, slotsRes] = await Promise.all([
            api.get(`${apiBase}/metadata/${id}`),
            api.get(`${apiBase}/register/${id}/available-slots/`),
          ]);
          result[id] = {
            is_restricted: metadataRes.data.is_restricted,
            slots: metadataRes.data.slots,
            registered: slotsRes.data.registered,
          };
        } catch {
          result[id] = null;
        }
      }),
    );
    setActivityData(result);
  };

  const handleMetadataUpdate = async (activityId) => {
    try {
      const [metadataRes, slotsRes] = await Promise.all([
        api.get(`${apiBase}/metadata/${activityId}`),
        api.get(`${apiBase}/register/${activityId}/available-slots/`),
      ]);
      setActivityData((prev) => ({
        ...prev,
        [activityId]: {
          is_restricted: metadataRes.data.is_restricted,
          slots: metadataRes.data.slots,
          registered: slotsRes.data.registered,
        },
      }));
    } catch (err) {
      console.error("Error:", err);
    }
  };

  const mappedActivities = activities.map((activity) => ({
    ...activity,
    type: getActivityType(activity.type_id),
    metadata: activityData[activity.id],
  }));

  const selectedActivity = activities.find((a) => a.id === selectedActivityId);

  return (
    <div className="w-full min-h-svh p-4 lg:p-8">
      <h1 className="text-3xl font-bold mb-6">{t("activities.editSlotsTitle")}</h1>

      {isLoadingData ? (
        <div className="flex justify-center items-center h-64">
          <span className="loading loading-spinner loading-lg" />
        </div>
      ) : mappedActivities.length === 0 ? (
        <div className="text-center py-12">
          <FaSearch className="mx-auto text-4xl text-gray-400 mb-4" />
          <p className="text-2xl text-gray-500">{t("activities.noActivities")}</p>
        </div>
      ) : (
        <div className="w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-6">
          {mappedActivities.map((activity) => (
            <ActivityCard
              key={activity.id}
              activity={activity}
              onEdit={(id) => setSelectedActivityId(id)}
            />
          ))}
        </div>
      )}

      {selectedActivityId && (
        <EditMetadataModal
          activityId={selectedActivityId}
          activityName={selectedActivity?.name}
          onUpdate={handleMetadataUpdate}
          onClose={() => setSelectedActivityId(null)}
        />
      )}
    </div>
  );
}

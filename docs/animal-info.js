import {ANIMAL_PROFILES,describeBehavior,compactBehavior} from './animal-profiles.js?v=20261016au';

/** Read-only companion shared by all species; never dispatches animal actions. */
export function createAnimalInfo(panel,announcement){
  const title=panel.querySelector('[data-species]'),scientific=panel.querySelector('[data-scientific]'),intro=panel.querySelector('[data-intro]');
  const facts=panel.querySelector('[data-facts]'),source=panel.querySelector('[data-source]');
  const status=panel.querySelector('[data-behavior]'),description=panel.querySelector('[data-behavior-description]'),place=panel.querySelector('[data-place]');
  const behavior=panel.querySelector('.animal-behavior');
  const summary=panel.querySelector('[data-summary]'),shortDescription=panel.querySelector('[data-short-description]');
  let species=null,signature='';
  return {
    show(key){
      const profile=ANIMAL_PROFILES[key];panel.hidden=!profile;signature='';behavior.hidden=true;
      if(!profile){species=null;return;}
      if(species!==key){
        title.textContent=profile.name;scientific.textContent=profile.scientific;intro.textContent=profile.description;summary.textContent=profile.summary;source.href=profile.source;
        facts.replaceChildren(...profile.facts.map(([label,value])=>{
          const group=document.createElement('div'),term=document.createElement('dt'),definition=document.createElement('dd');
          term.textContent=label;definition.textContent=value;group.append(term,definition);return group;
        }));
      }
      species=key;panel.dataset.species=key;panel.dataset.activity='colony';
    },
    update(detail){
      if(panel.hidden)return;
      behavior.hidden=!detail;
      if(!detail){signature='';panel.dataset.activity='colony';return;}
      const [name,text]=describeBehavior(species,detail),next=[detail.label,name].join('|');
      if(next===signature)return;signature=next;
      status.textContent=name;description.textContent=text;place.textContent=detail.label;
      announcement.textContent=detail.label+': '+name+'.';
      shortDescription.textContent=compactBehavior(species,detail);
      panel.dataset.activity=detail.activity||'rest';
    },
  };
}
